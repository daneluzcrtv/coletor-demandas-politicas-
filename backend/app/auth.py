from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Assessor

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)


def criar_token(assessor_id: int, nome: str, cargo: str) -> str:
    expira = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(assessor_id), "nome": nome, "cargo": cargo, "exp": expira},
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Assessor:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        assessor_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise erro

    assessor = await db.get(Assessor, assessor_id)
    if not assessor or not assessor.ativo:
        raise erro
    return assessor


async def require_deputado(assessor: Assessor = Depends(get_current_user)) -> Assessor:
    if assessor.cargo != "deputado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o deputado pode realizar esta ação.",
        )
    return assessor
