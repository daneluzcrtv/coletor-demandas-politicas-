from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_deputado
from app.database import get_db
from app.models import Assessor, Bairro
from app.schemas import BairroCreate, BairroOut, BairroUpdate

router = APIRouter()


@router.get("/", response_model=list[BairroOut])
async def listar_bairros(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bairro).order_by(Bairro.nome))
    return result.scalars().all()


@router.get("/{id}", response_model=BairroOut)
async def obter_bairro(id: int, db: AsyncSession = Depends(get_db)):
    bairro = await db.get(Bairro, id)
    if not bairro:
        raise HTTPException(404, "Bairro não encontrado")
    return bairro


@router.post("/", response_model=BairroOut, status_code=201)
async def criar_bairro(
    payload: BairroCreate,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    bairro = Bairro(**payload.model_dump())
    db.add(bairro)
    await db.commit()
    await db.refresh(bairro)
    return bairro


@router.patch("/{id}", response_model=BairroOut)
async def atualizar_bairro(
    id: int,
    payload: BairroUpdate,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    bairro = await db.get(Bairro, id)
    if not bairro:
        raise HTTPException(404, "Bairro não encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(bairro, campo, valor)
    await db.commit()
    await db.refresh(bairro)
    return bairro


@router.delete("/{id}", status_code=204)
async def deletar_bairro(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    bairro = await db.get(Bairro, id)
    if not bairro:
        raise HTTPException(404, "Bairro não encontrado")
    await db.delete(bairro)
    await db.commit()
