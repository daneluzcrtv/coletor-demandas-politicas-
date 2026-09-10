from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from app.database import engine, Base, AsyncSessionLocal


CONTAS_DEMO = [
    {"nome": "Deputado",  "email": "deputado@gabinete.com",  "senha": "demo123", "cargo": "deputado"},
    {"nome": "Assessor",  "email": "assessor@gabinete.com",  "senha": "demo123", "cargo": "assessor"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(
            "ALTER TABLE assessor ADD COLUMN IF NOT EXISTS senha_hash TEXT"
        ))
        await conn.execute(text(
            "ALTER TABLE assessor ADD COLUMN IF NOT EXISTS cargo TEXT DEFAULT 'assessor'"
        ))

    # Cria contas de demonstração e garante cargo correto
    from app.models import Assessor
    from app.auth import hash_senha
    async with AsyncSessionLocal() as db:
        for conta in CONTAS_DEMO:
            result = await db.execute(select(Assessor).where(Assessor.email == conta["email"]))
            assessor = result.scalar_one_or_none()
            if not assessor:
                db.add(Assessor(
                    nome=conta["nome"],
                    email=conta["email"],
                    senha_hash=hash_senha(conta["senha"]),
                    cargo=conta["cargo"],
                    ativo=True,
                ))
            else:
                assessor.cargo = conta["cargo"]
        await db.commit()

    yield


app = FastAPI(
    title="Coletor de Demandas Políticas",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Depends  # noqa: E402
from app.auth import get_current_user  # noqa: E402
from app.routes import demandas, cidadaos, assessores, bairros, relatorio, bot, simulador, analise, acompanhamento  # noqa: E402
from app.routes import auth  # noqa: E402

_auth = [Depends(get_current_user)]

# Rotas públicas
app.include_router(auth.router,     prefix="/auth", tags=["auth"])
app.include_router(bot.router,      prefix="/bot",  tags=["bot"])   # webhook chamado pela Meta

# Rotas protegidas
app.include_router(demandas.router,      prefix="/demandas",      tags=["demandas"],      dependencies=_auth)
app.include_router(cidadaos.router,      prefix="/cidadaos",      tags=["cidadaos"],      dependencies=_auth)
app.include_router(assessores.router,    prefix="/assessores",    tags=["assessores"],    dependencies=_auth)
app.include_router(bairros.router,       prefix="/bairros",       tags=["bairros"],       dependencies=_auth)
app.include_router(relatorio.router,     prefix="/relatorio",     tags=["relatorio"],     dependencies=_auth)
app.include_router(simulador.router,     prefix="/simular",       tags=["simulador"],     dependencies=_auth)
app.include_router(analise.router,       prefix="/analise",       tags=["analise"],       dependencies=_auth)
app.include_router(acompanhamento.router,prefix="/acompanhamento",tags=["acompanhamento"],dependencies=_auth)


@app.get("/health")
async def health():
    return {"status": "ok"}
