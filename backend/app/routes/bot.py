import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Cidadao, Demanda, InteracaoBot
from app.bot.agente import processar
from app.services.whatsapp import send_text
from app.services.geocoding import geocodificar
from app.services.roteamento import encontrar_bairro, encontrar_assessor
from app.services.notificacao import notificar_assessor_nova_demanda

router = APIRouter()


# ── Verificação do webhook (Meta chama uma vez ao cadastrar) ──────────────────

@router.get("/webhook")
async def verificar_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    # Bug corrigido: Meta exige plain text, não JSON
    if hub_mode != "subscribe" or hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(403, "Token de verificação inválido")
    return PlainTextResponse(content=hub_challenge)


# ── Recebimento de mensagens ──────────────────────────────────────────────────

@router.post("/webhook")
async def receber_mensagem(request: Request, db: AsyncSession = Depends(get_db)):
    payload: dict[str, Any] = await request.json()

    try:
        entry = payload["entry"][0]["changes"][0]["value"]
        mensagens = entry.get("messages", [])
    except (KeyError, IndexError):
        # Notificação de status (lida, entregue etc.) — ignorar
        return {"status": "ignored"}

    for msg in mensagens:
        wa_id: str = msg["from"]
        tipo: str = msg["type"]

        texto_cidadao: str = ""
        latitude: float | None = None
        longitude: float | None = None

        if tipo == "text":
            texto_cidadao = msg["text"]["body"]
        elif tipo == "location":
            latitude = msg["location"]["latitude"]
            longitude = msg["location"]["longitude"]
            texto_cidadao = "[localização]"
        else:
            await send_text(wa_id, "Por enquanto só consigo receber texto e localização. Pode digitar sua mensagem?")
            continue

        cidadao = await _obter_ou_criar_cidadao(wa_id, db)

        # Bug corrigido: processar() ANTES de salvar qualquer interação.
        # Assim o histórico carregado não inclui a mensagem atual, e o
        # objeto cidadao não expira por um commit intermediário.
        resultado = await processar(
            wa_id=wa_id,
            mensagem_cidadao=texto_cidadao,
            db=db,
            latitude=latitude,
            longitude=longitude,
        )

        assessor_notif = None
        bairro_notif = None
        if resultado.dados_demanda:
            protocolo, assessor_notif, bairro_notif = await _registrar_demanda(cidadao, resultado.dados_demanda, db)
            resposta_final = (
                resultado.resposta_texto.replace("{protocolo}", protocolo)
                if "{protocolo}" in resultado.resposta_texto
                else resultado.resposta_texto + f"\n\nProtocolo: *#{protocolo}*"
            )
        else:
            resposta_final = resultado.resposta_texto

        # Salva as duas interações e faz um único commit no final
        db.add(InteracaoBot(cidadao_id=cidadao.id, mensagem=texto_cidadao, remetente="cidadao"))
        db.add(InteracaoBot(cidadao_id=cidadao.id, mensagem=resposta_final, remetente="bot"))
        await db.commit()

        await send_text(wa_id, resposta_final)

        # Notifica assessor após commit (falha não bloqueia o fluxo)
        if assessor_notif and resultado.dados_demanda:
            await notificar_assessor_nova_demanda(
                assessor=assessor_notif,
                protocolo=protocolo,
                nome_cidadao=cidadao.nome,
                bairro_nome=bairro_notif.nome if bairro_notif else None,
                categoria=resultado.dados_demanda.get("categoria"),
                resumo=resultado.dados_demanda.get("resumo"),
            )

    return {"status": "ok"}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _obter_ou_criar_cidadao(wa_id: str, db: AsyncSession) -> Cidadao:
    result = await db.execute(select(Cidadao).where(Cidadao.wa_id == wa_id))
    cidadao = result.scalar_one_or_none()
    if not cidadao:
        cidadao = Cidadao(wa_id=wa_id, nome="Desconhecido")
        db.add(cidadao)
        await db.flush()  # garante o id sem fechar a transação
    return cidadao


async def _registrar_demanda(cidadao: Cidadao, dados: dict, db: AsyncSession):
    """Retorna (protocolo, assessor | None, bairro | None)."""
    protocolo = f"DEM{uuid.uuid4().hex[:8].upper()}"

    lat: float | None = dados.get("latitude")
    lon: float | None = dados.get("longitude")
    endereco_texto: str | None = dados.get("endereco_texto")

    if endereco_texto and not lat:
        coords = await geocodificar(endereco_texto)
        if coords:
            lat, lon = coords

    if dados.get("nome"):
        cidadao.nome = dados["nome"]
    if not cidadao.endereco_texto and endereco_texto:
        cidadao.endereco_texto = endereco_texto
    if not cidadao.latitude and lat:
        cidadao.latitude = lat
        cidadao.longitude = lon

    cidadao.total_demandas += 1

    bairro_obj = None
    assessor_obj = None
    bairro_id: int | None = None
    assessor_id: int | None = None

    if lat and lon:
        bairro_obj = await encontrar_bairro(lat, lon, db)
        if bairro_obj:
            bairro_id = bairro_obj.id
            if not cidadao.bairro_id:
                cidadao.bairro_id = bairro_id
            assessor_obj = await encontrar_assessor(bairro_obj, dados.get("categoria"), db)
            if assessor_obj:
                assessor_id = assessor_obj.id

    db.add(Demanda(
        cidadao_id=cidadao.id,
        descricao=dados.get("descricao", ""),
        categoria=dados.get("categoria"),
        resumo=dados.get("resumo"),
        bairro_id=bairro_id,
        latitude=lat,
        longitude=lon,
        assessor_responsavel_id=assessor_id,
        protocolo=protocolo,
        canal_origem="whatsapp",
    ))
    # commit acontece no chamador (receber_mensagem), junto com as interações
    return protocolo, assessor_obj, bairro_obj
