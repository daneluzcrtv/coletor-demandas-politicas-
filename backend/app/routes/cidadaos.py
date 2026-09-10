from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Cidadao, Demanda
from app.schemas import CidadaoCreate, CidadaoOut, CidadaoUpdate, DemandaOut

router = APIRouter()


@router.get("/", response_model=list[CidadaoOut])
async def listar_cidadaos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cidadao).order_by(Cidadao.nome))
    return result.scalars().all()


@router.get("/{id}", response_model=CidadaoOut)
async def obter_cidadao(id: int, db: AsyncSession = Depends(get_db)):
    cidadao = await db.get(Cidadao, id)
    if not cidadao:
        raise HTTPException(404, "Cidadão não encontrado")
    return cidadao


@router.get("/{id}/demandas", response_model=list[DemandaOut])
async def demandas_do_cidadao(id: int, db: AsyncSession = Depends(get_db)):
    cidadao = await db.get(Cidadao, id)
    if not cidadao:
        raise HTTPException(404, "Cidadão não encontrado")
    result = await db.execute(
        select(Demanda)
        .where(Demanda.cidadao_id == id)
        .order_by(Demanda.data_abertura.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=CidadaoOut, status_code=201)
async def criar_cidadao(payload: CidadaoCreate, db: AsyncSession = Depends(get_db)):
    cidadao = Cidadao(**payload.model_dump())
    db.add(cidadao)
    await db.commit()
    await db.refresh(cidadao)
    return cidadao


@router.patch("/{id}", response_model=CidadaoOut)
async def atualizar_cidadao(
    id: int, payload: CidadaoUpdate, db: AsyncSession = Depends(get_db)
):
    cidadao = await db.get(Cidadao, id)
    if not cidadao:
        raise HTTPException(404, "Cidadão não encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(cidadao, campo, valor)
    await db.commit()
    await db.refresh(cidadao)
    return cidadao
