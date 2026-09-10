from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Cidadao, InteracaoBot
from app.bot.agente import processar
from app.routes.bot import _obter_ou_criar_cidadao, _registrar_demanda

router = APIRouter()


class MensagemSimulada(BaseModel):
    wa_id: str = "5500000000000"   # número fictício para o simulador
    mensagem: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RespostaSimulada(BaseModel):
    resposta: str
    demanda_registrada: bool
    protocolo: Optional[str] = None


@router.post("/", response_model=RespostaSimulada)
async def simular_mensagem(payload: MensagemSimulada, db: AsyncSession = Depends(get_db)):
    """
    Simula uma mensagem recebida pelo WhatsApp.
    Roda o fluxo completo do agente e retorna a resposta do bot.
    """
    cidadao = await _obter_ou_criar_cidadao(payload.wa_id, db)

    resultado = await processar(
        wa_id=payload.wa_id,
        mensagem_cidadao=payload.mensagem,
        db=db,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )

    protocolo = None
    if resultado.dados_demanda:
        protocolo = await _registrar_demanda(cidadao, resultado.dados_demanda, db)
        resposta_final = (
            resultado.resposta_texto.replace("{protocolo}", protocolo)
            if "{protocolo}" in resultado.resposta_texto
            else resultado.resposta_texto + f"\n\nProtocolo: #{protocolo}"
        )
    else:
        resposta_final = resultado.resposta_texto

    db.add(InteracaoBot(cidadao_id=cidadao.id, mensagem=payload.mensagem, remetente="cidadao"))
    db.add(InteracaoBot(cidadao_id=cidadao.id, mensagem=resposta_final, remetente="bot"))
    await db.commit()

    return RespostaSimulada(
        resposta=resposta_final,
        demanda_registrada=resultado.dados_demanda is not None,
        protocolo=protocolo,
    )


@router.get("/historico/{wa_id}")
async def historico(wa_id: str, db: AsyncSession = Depends(get_db)):
    """Retorna o histórico completo de uma conversa pelo wa_id."""
    result = await db.execute(select(Cidadao).where(Cidadao.wa_id == wa_id))
    cidadao = result.scalar_one_or_none()
    if not cidadao:
        return []

    result = await db.execute(
        select(InteracaoBot)
        .where(InteracaoBot.cidadao_id == cidadao.id)
        .order_by(InteracaoBot.timestamp)
    )
    return [
        {"remetente": i.remetente, "mensagem": i.mensagem, "timestamp": i.timestamp}
        for i in result.scalars().all()
    ]
