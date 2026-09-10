from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import criar_token, get_current_user, verificar_senha
from app.database import get_db
from app.models import Assessor

router = APIRouter()


class LoginInput(BaseModel):
    email: str
    senha: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nome: str
    assessor_id: int
    cargo: str


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginInput, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assessor).where(Assessor.email == payload.email))
    assessor = result.scalar_one_or_none()

    if not assessor or not assessor.senha_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos")
    if not verificar_senha(payload.senha, assessor.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos")
    if not assessor.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Conta inativa")

    cargo = assessor.cargo or "assessor"
    return TokenOut(
        access_token=criar_token(assessor.id, assessor.nome, cargo),
        nome=assessor.nome,
        assessor_id=assessor.id,
        cargo=cargo,
    )


@router.get("/me")
async def me(assessor: Assessor = Depends(get_current_user)):
    return {
        "id": assessor.id,
        "nome": assessor.nome,
        "email": assessor.email,
        "cargo": assessor.cargo or "assessor",
        "areas_tematicas": assessor.areas_tematicas,
    }
