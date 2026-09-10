import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Acompanhamento, Assessor, Bairro, Cidadao, Demanda, FotoAcompanhamento, InteracaoBot
from app.schemas import DemandaCreate, DemandaOut, DemandaUpdate
from app.services.notificacao import notificar_assessor_nova_demanda

router = APIRouter()

STATUS_VALIDOS = {"aberta", "em_andamento", "concluida"}


@router.get("/", response_model=list[DemandaOut])
async def listar_demandas(
    status: Optional[str] = Query(None),
    bairro_id: Optional[int] = Query(None),
    categoria: Optional[str] = Query(None),
    assessor_id: Optional[int] = Query(None),
    busca: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Demanda).order_by(Demanda.data_abertura.desc())
    if status:
        query = query.where(Demanda.status == status)
    if bairro_id:
        query = query.where(Demanda.bairro_id == bairro_id)
    if categoria:
        query = query.where(Demanda.categoria == categoria)
    if assessor_id:
        query = query.where(Demanda.assessor_responsavel_id == assessor_id)
    if busca:
        query = query.outerjoin(Demanda.cidadao).where(
            or_(
                Demanda.protocolo.ilike(f"%{busca}%"),
                Cidadao.nome.ilike(f"%{busca}%"),
            )
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{id}/detalhe")
async def detalhe_demanda(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Demanda)
        .options(
            selectinload(Demanda.cidadao),
            selectinload(Demanda.bairro),
            selectinload(Demanda.assessor_responsavel),
            selectinload(Demanda.acompanhamentos).selectinload(Acompanhamento.fotos),
        )
        .where(Demanda.id == id)
    )
    demanda = result.scalar_one_or_none()
    if not demanda:
        raise HTTPException(404, "Demanda não encontrada")

    interacoes = []
    if demanda.cidadao_id:
        res = await db.execute(
            select(InteracaoBot)
            .where(InteracaoBot.cidadao_id == demanda.cidadao_id)
            .order_by(InteracaoBot.timestamp)
        )
        interacoes = res.scalars().all()

    return {
        "id": demanda.id,
        "protocolo": demanda.protocolo,
        "categoria": demanda.categoria,
        "resumo": demanda.resumo,
        "descricao": demanda.descricao,
        "status": demanda.status,
        "canal_origem": demanda.canal_origem,
        "data_abertura": demanda.data_abertura,
        "data_conclusao": demanda.data_conclusao,
        "latitude": demanda.latitude,
        "longitude": demanda.longitude,
        "cidadao": {
            "id": demanda.cidadao.id,
            "nome": demanda.cidadao.nome,
            "wa_id": demanda.cidadao.wa_id,
            "telefone": demanda.cidadao.telefone,
            "endereco_texto": demanda.cidadao.endereco_texto,
            "total_demandas": demanda.cidadao.total_demandas,
            "data_cadastro": demanda.cidadao.data_cadastro,
        } if demanda.cidadao else None,
        "bairro": {
            "id": demanda.bairro.id,
            "nome": demanda.bairro.nome,
            "zona": demanda.bairro.zona,
        } if demanda.bairro else None,
        "assessor": {
            "id": demanda.assessor_responsavel.id,
            "nome": demanda.assessor_responsavel.nome,
            "telefone": demanda.assessor_responsavel.telefone,
            "email": demanda.assessor_responsavel.email,
            "areas_tematicas": demanda.assessor_responsavel.areas_tematicas,
        } if demanda.assessor_responsavel else None,
        "conversa": [
            {"remetente": i.remetente, "mensagem": i.mensagem, "timestamp": str(i.timestamp)}
            for i in interacoes
        ],
        "acompanhamentos": [
            {
                "id": a.id,
                "tipo": a.tipo,
                "descricao": a.descricao,
                "autor": a.autor,
                "data": str(a.data),
                "fotos": [{"id": f.id, "nome_arquivo": f.nome_arquivo} for f in a.fotos],
            }
            for a in demanda.acompanhamentos
        ],
    }


@router.get("/{id}", response_model=DemandaOut)
async def obter_demanda(id: int, db: AsyncSession = Depends(get_db)):
    demanda = await db.get(Demanda, id)
    if not demanda:
        raise HTTPException(404, "Demanda não encontrada")
    return demanda


@router.post("/", response_model=DemandaOut, status_code=201)
async def criar_demanda(payload: DemandaCreate, db: AsyncSession = Depends(get_db)):
    protocolo = f"DEM{uuid.uuid4().hex[:8].upper()}"
    demanda = Demanda(**payload.model_dump(), protocolo=protocolo)
    db.add(demanda)

    if payload.cidadao_id:
        cidadao = await db.get(Cidadao, payload.cidadao_id)
        if cidadao:
            cidadao.total_demandas += 1

    await db.commit()
    await db.refresh(demanda)
    return demanda


@router.patch("/{id}", response_model=DemandaOut)
async def atualizar_demanda(
    id: int, payload: DemandaUpdate, db: AsyncSession = Depends(get_db)
):
    demanda = await db.get(Demanda, id)
    if not demanda:
        raise HTTPException(404, "Demanda não encontrada")

    dados = payload.model_dump(exclude_unset=True)

    if "status" in dados and dados["status"] not in STATUS_VALIDOS:
        raise HTTPException(400, f"Status inválido. Use: {STATUS_VALIDOS}")

    if dados.get("status") == "concluida" and not demanda.data_conclusao:
        dados["data_conclusao"] = datetime.utcnow()

    assessor_anterior_id = demanda.assessor_responsavel_id

    for campo, valor in dados.items():
        setattr(demanda, campo, valor)

    await db.commit()
    await db.refresh(demanda)

    # Notifica assessor se foi atribuído agora pela primeira vez ou trocado
    novo_id = dados.get("assessor_responsavel_id")
    if novo_id and novo_id != assessor_anterior_id:
        assessor = await db.get(Assessor, novo_id)
        if assessor:
            bairro = await db.get(Bairro, demanda.bairro_id) if demanda.bairro_id else None
            cidadao = await db.get(Cidadao, demanda.cidadao_id) if demanda.cidadao_id else None
            await notificar_assessor_nova_demanda(
                assessor=assessor,
                protocolo=demanda.protocolo or str(demanda.id),
                nome_cidadao=cidadao.nome if cidadao else "Cidadão",
                bairro_nome=bairro.nome if bairro else None,
                categoria=demanda.categoria,
                resumo=demanda.resumo,
            )

    return demanda
