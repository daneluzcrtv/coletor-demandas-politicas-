from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/mensal")
async def relatorio_mensal(
    mes: Optional[str] = Query(None, description="Mês no formato YYYY-MM. Padrão: mês atual."),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna estatísticas do mês agrupadas por bairro/categoria, por assessor e totais gerais.
    """
    # Define o intervalo do mês
    if mes:
        inicio = date.fromisoformat(f"{mes}-01")
    else:
        hoje = date.today()
        inicio = date(hoje.year, hoje.month, 1)

    params = {"inicio": inicio}

    # ── 1. Por bairro e categoria ─────────────────────────────────────────────
    por_bairro = await db.execute(
        text("""
            SELECT
                COALESCE(b.nome, 'Não identificado') AS bairro,
                COALESCE(d.categoria, 'outro')        AS categoria,
                COUNT(*)                              AS total,
                COUNT(*) FILTER (WHERE d.status = 'concluida') AS concluidas,
                ROUND(
                    AVG(
                        EXTRACT(EPOCH FROM (d.data_conclusao - d.data_abertura)) / 86400
                    ) FILTER (WHERE d.data_conclusao IS NOT NULL),
                    1
                )                                     AS media_dias_resolucao
            FROM demanda d
            LEFT JOIN bairro b ON b.id = d.bairro_id
            WHERE d.data_abertura >= :inicio
              AND d.data_abertura <  :inicio + INTERVAL '1 month'
            GROUP BY b.nome, d.categoria
            ORDER BY total DESC
        """),
        params,
    )

    # ── 2. Por assessor ───────────────────────────────────────────────────────
    por_assessor = await db.execute(
        text("""
            SELECT
                COALESCE(a.nome, 'Sem assessor')      AS assessor,
                COUNT(*)                              AS total,
                COUNT(*) FILTER (WHERE d.status = 'aberta')       AS abertas,
                COUNT(*) FILTER (WHERE d.status = 'em_andamento') AS em_andamento,
                COUNT(*) FILTER (WHERE d.status = 'concluida')    AS concluidas
            FROM demanda d
            LEFT JOIN assessor a ON a.id = d.assessor_responsavel_id
            WHERE d.data_abertura >= :inicio
              AND d.data_abertura <  :inicio + INTERVAL '1 month'
            GROUP BY a.nome
            ORDER BY total DESC
        """),
        params,
    )

    # ── 3. Totais gerais do mês ───────────────────────────────────────────────
    totais = await db.execute(
        text("""
            SELECT
                COUNT(*)                                          AS total_demandas,
                COUNT(*) FILTER (WHERE status = 'aberta')        AS abertas,
                COUNT(*) FILTER (WHERE status = 'em_andamento')  AS em_andamento,
                COUNT(*) FILTER (WHERE status = 'concluida')     AS concluidas,
                COUNT(DISTINCT cidadao_id)                       AS cidadaos_atendidos,
                ROUND(
                    AVG(
                        EXTRACT(EPOCH FROM (data_conclusao - data_abertura)) / 86400
                    ) FILTER (WHERE data_conclusao IS NOT NULL),
                    1
                )                                                AS media_dias_resolucao
            FROM demanda
            WHERE data_abertura >= :inicio
              AND data_abertura <  :inicio + INTERVAL '1 month'
        """),
        params,
    )

    total_row = totais.mappings().one()

    return {
        "mes_referencia": inicio.strftime("%Y-%m"),
        "totais": dict(total_row),
        "por_bairro_categoria": [dict(r) for r in por_bairro.mappings().all()],
        "por_assessor": [dict(r) for r in por_assessor.mappings().all()],
    }
