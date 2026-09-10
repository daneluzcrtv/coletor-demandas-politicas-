from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_senha, require_deputado
from app.database import get_db
from app.models import Assessor
from app.schemas import AssessorCreate, AssessorOut, AssessorUpdate

router = APIRouter()


@router.get("/", response_model=list[AssessorOut])
async def listar_assessores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assessor).order_by(Assessor.nome))
    return result.scalars().all()


@router.get("/{id}", response_model=AssessorOut)
async def obter_assessor(id: int, db: AsyncSession = Depends(get_db)):
    assessor = await db.get(Assessor, id)
    if not assessor:
        raise HTTPException(404, "Assessor não encontrado")
    return assessor


@router.post("/", response_model=AssessorOut, status_code=201)
async def criar_assessor(
    payload: AssessorCreate,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    assessor = Assessor(**payload.model_dump())
    db.add(assessor)
    await db.commit()
    await db.refresh(assessor)
    return assessor


@router.patch("/{id}", response_model=AssessorOut)
async def atualizar_assessor(
    id: int,
    payload: AssessorUpdate,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    assessor = await db.get(Assessor, id)
    if not assessor:
        raise HTTPException(404, "Assessor não encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(assessor, campo, valor)
    await db.commit()
    await db.refresh(assessor)
    return assessor


@router.delete("/{id}", status_code=204)
async def deletar_assessor(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    assessor = await db.get(Assessor, id)
    if not assessor:
        raise HTTPException(404, "Assessor não encontrado")
    await db.delete(assessor)
    await db.commit()


class SenhaInput(BaseModel):
    senha: str


@router.post("/{id}/senha", status_code=204)
async def definir_senha(
    id: int,
    payload: SenhaInput,
    db: AsyncSession = Depends(get_db),
    _: Assessor = Depends(require_deputado),
):
    assessor = await db.get(Assessor, id)
    if not assessor:
        raise HTTPException(404, "Assessor não encontrado")
    if len(payload.senha) < 6:
        raise HTTPException(400, "A senha deve ter no mínimo 6 caracteres")
    assessor.senha_hash = hash_senha(payload.senha)
    await db.commit()
