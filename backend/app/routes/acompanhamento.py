from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Acompanhamento, Demanda, FotoAcompanhamento

router = APIRouter()

TIPOS_VALIDOS = {
    "nota", "visita", "contato", "encaminhamento",
    "resolucao_parcial", "conclusao",
}


@router.get("/demanda/{demanda_id}")
async def listar_acompanhamentos(demanda_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Acompanhamento)
        .options(selectinload(Acompanhamento.fotos))
        .where(Acompanhamento.demanda_id == demanda_id)
        .order_by(Acompanhamento.data)
    )
    items = result.scalars().all()
    return [_serializar(a) for a in items]


@router.post("/demanda/{demanda_id}", status_code=201)
async def criar_acompanhamento(
    demanda_id: int,
    descricao: str = Form(...),
    tipo: str = Form("nota"),
    autor: Optional[str] = Form(None),
    fotos: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    demanda = await db.get(Demanda, demanda_id)
    if not demanda:
        raise HTTPException(404, "Demanda não encontrada")

    if tipo not in TIPOS_VALIDOS:
        raise HTTPException(400, f"Tipo inválido. Use: {sorted(TIPOS_VALIDOS)}")

    acomp = Acompanhamento(
        demanda_id=demanda_id,
        descricao=descricao,
        tipo=tipo,
        autor=autor or "Assessoria",
    )
    db.add(acomp)
    await db.flush()

    for arquivo in fotos:
        conteudo = await arquivo.read()
        if not conteudo:
            continue
        foto = FotoAcompanhamento(
            acompanhamento_id=acomp.id,
            nome_arquivo=arquivo.filename or "foto.jpg",
            mime_type=arquivo.content_type or "image/jpeg",
            dados=conteudo,
        )
        db.add(foto)

    await db.commit()
    await db.refresh(acomp)

    result = await db.execute(
        select(Acompanhamento)
        .options(selectinload(Acompanhamento.fotos))
        .where(Acompanhamento.id == acomp.id)
    )
    return _serializar(result.scalar_one())


@router.delete("/{id}", status_code=204)
async def deletar_acompanhamento(id: int, db: AsyncSession = Depends(get_db)):
    acomp = await db.get(Acompanhamento, id)
    if not acomp:
        raise HTTPException(404, "Acompanhamento não encontrado")
    await db.delete(acomp)
    await db.commit()


@router.get("/foto/{foto_id}")
async def servir_foto(foto_id: int, db: AsyncSession = Depends(get_db)):
    foto = await db.get(FotoAcompanhamento, foto_id)
    if not foto:
        raise HTTPException(404, "Foto não encontrada")
    return Response(content=foto.dados, media_type=foto.mime_type)


def _serializar(a: Acompanhamento) -> dict:
    return {
        "id": a.id,
        "demanda_id": a.demanda_id,
        "tipo": a.tipo,
        "descricao": a.descricao,
        "autor": a.autor,
        "data": str(a.data),
        "fotos": [
            {"id": f.id, "nome_arquivo": f.nome_arquivo, "mime_type": f.mime_type}
            for f in a.fotos
        ],
    }
