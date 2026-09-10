from typing import Optional
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings

router = APIRouter()

_CHAVE_VALIDA = (
    settings.anthropic_api_key.startswith("sk-ant-")
    and len(settings.anthropic_api_key) > 20
)


@router.get("/eleitoral")
async def analise_eleitoral(
    mes: Optional[str] = Query(None, description="YYYY-MM. Padrão: últimos 6 meses"),
    db: AsyncSession = Depends(get_db),
):
    """
    Gera análise eleitoral com base nos padrões de demandas por bairro.
    Usa Claude se a chave estiver configurada, senão retorna análise baseada em regras.
    """
    dados = await _coletar_dados(db, mes)

    if _CHAVE_VALIDA:
        analise = await _analisar_com_claude(dados)
    else:
        analise = _analisar_com_regras(dados)

    return {
        "dados_brutos": dados,
        "analise": analise,
    }


@router.get("/simular")
async def simular_cenario(
    bairro: str = Query(..., description="Nome do bairro"),
    acao: str = Query(..., description="Ação hipotética do candidato"),
    db: AsyncSession = Depends(get_db),
):
    """
    Simula o impacto eleitoral de uma ação específica em um bairro.
    """
    dados = await _coletar_dados(db)
    bairro_dados = next(
        (b for b in dados["por_bairro"] if bairro.lower() in b["bairro"].lower()),
        None,
    )

    if not bairro_dados:
        return {"erro": f"Bairro '{bairro}' não encontrado nos dados de demandas."}

    if _CHAVE_VALIDA:
        simulacao = await _simular_com_claude(bairro, acao, bairro_dados, dados["totais"])
    else:
        simulacao = _simular_com_regras(bairro, acao, bairro_dados, dados["totais"])

    return {"bairro": bairro, "acao": acao, "simulacao": simulacao}


# ── Coleta de dados do banco ──────────────────────────────────────────────────

async def _coletar_dados(db: AsyncSession, mes: Optional[str] = None) -> dict:
    filtro_data = ""
    params = {}
    if mes:
        filtro_data = "WHERE d.data_abertura >= :inicio AND d.data_abertura < :inicio::date + INTERVAL '1 month'"
        params["inicio"] = f"{mes}-01"

    por_bairro = await db.execute(text(f"""
        SELECT
            COALESCE(b.nome, 'Não identificado') AS bairro,
            COUNT(*)                              AS total_demandas,
            COUNT(*) FILTER (WHERE d.status = 'concluida') AS concluidas,
            COUNT(*) FILTER (WHERE d.status = 'aberta')    AS abertas,
            MODE() WITHIN GROUP (ORDER BY d.categoria)     AS categoria_principal,
            json_object_agg(
                COALESCE(d.categoria, 'outro'),
                COUNT(*)
            )                                              AS por_categoria
        FROM demanda d
        LEFT JOIN bairro b ON b.id = d.bairro_id
        {filtro_data}
        GROUP BY b.nome
        ORDER BY total_demandas DESC
    """), params)

    totais = await db.execute(text(f"""
        SELECT
            COUNT(*)                                        AS total_demandas,
            COUNT(DISTINCT d.bairro_id)                    AS bairros_ativos,
            COUNT(DISTINCT d.cidadao_id)                   AS cidadaos_atendidos,
            COUNT(*) FILTER (WHERE d.status = 'concluida') AS concluidas,
            MODE() WITHIN GROUP (ORDER BY d.categoria)     AS categoria_mais_comum
        FROM demanda d
        {filtro_data}
    """), params)

    total_row = dict(totais.mappings().one())
    bairros_lista = [dict(r) for r in por_bairro.mappings().all()]

    # Calcula % do eleitorado estimado por bairro (placeholder até integrar dados TSE)
    total_geral = total_row["total_demandas"] or 1
    for b in bairros_lista:
        b["percentual_demandas"] = round((b["total_demandas"] / total_geral) * 100, 1)
        b["taxa_resolucao"] = (
            round((b["concluidas"] / b["total_demandas"]) * 100, 1)
            if b["total_demandas"] > 0 else 0
        )

    return {"totais": total_row, "por_bairro": bairros_lista}


# ── Análise com Claude ────────────────────────────────────────────────────────

async def _analisar_com_claude(dados: dict) -> dict:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    prompt = f"""Você é um especialista em análise eleitoral e gestão pública.
Analise os dados de demandas da cidade de Itapecerica da Serra e gere insights eleitorais estratégicos.

DADOS:
{json.dumps(dados, ensure_ascii=False, indent=2)}

Responda em JSON com exatamente esta estrutura:
{{
  "resumo_executivo": "2-3 frases resumindo o cenário",
  "pontos_criticos": [
    {{"bairro": "nome", "problema": "descrição", "urgencia": "alta|media|baixa", "impacto_eleitoral": "descrição"}}
  ],
  "oportunidades": [
    {{"bairro": "nome", "acao_sugerida": "descrição", "justificativa": "por que isso converte votos"}}
  ],
  "ranking_prioridade": ["bairro1", "bairro2", "bairro3"],
  "alerta": "algum padrão preocupante ou oportunidade urgente"
}}"""

    resposta = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    texto = resposta.content[0].text
    # Extrai JSON da resposta
    inicio = texto.find("{")
    fim = texto.rfind("}") + 1
    return json.loads(texto[inicio:fim])


async def _simular_com_claude(bairro: str, acao: str, bairro_dados: dict, totais: dict) -> dict:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    prompt = f"""Você é um especialista em ciência política e análise eleitoral.

CIDADE: Itapecerica da Serra
BAIRRO ANALISADO: {bairro}
DADOS DO BAIRRO: {json.dumps(bairro_dados, ensure_ascii=False)}
TOTAIS DA CIDADE: {json.dumps(totais, ensure_ascii=False)}
AÇÃO HIPOTÉTICA: "{acao}"

Simule o impacto eleitoral dessa ação. Responda em JSON:
{{
  "impacto_estimado": "alto|medio|baixo",
  "votos_potenciais": "estimativa narrativa (ex: 'entre 200 e 400 eleitores mobilizados')",
  "prazo_efeito": "imediato|curto_prazo|longo_prazo",
  "riscos": ["risco 1", "risco 2"],
  "acoes_complementares": ["ação adicional 1", "ação adicional 2"],
  "narrativa": "parágrafo explicando o cenário simulado"
}}"""

    resposta = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    texto = resposta.content[0].text
    inicio = texto.find("{")
    fim = texto.rfind("}") + 1
    return json.loads(texto[inicio:fim])


# ── Análise baseada em regras (sem API) ──────────────────────────────────────

def _analisar_com_regras(dados: dict) -> dict:
    bairros = dados["por_bairro"]
    if not bairros:
        return {"resumo_executivo": "Nenhuma demanda registrada ainda.", "pontos_criticos": [], "oportunidades": [], "ranking_prioridade": [], "alerta": ""}

    criticos = [b for b in bairros if b["abertas"] > 0 and b["taxa_resolucao"] < 30]
    oportunidades = [b for b in bairros if b["taxa_resolucao"] >= 50]

    return {
        "resumo_executivo": (
            f"Foram registradas {dados['totais']['total_demandas']} demandas em "
            f"{dados['totais']['bairros_ativos']} bairros. "
            f"O bairro com mais demandas é {bairros[0]['bairro']} ({bairros[0]['total_demandas']} registros). "
            "Ative a análise com IA para insights eleitorais detalhados."
        ),
        "pontos_criticos": [
            {"bairro": b["bairro"], "problema": f"{b['abertas']} demandas abertas sem resolução", "urgencia": "alta", "impacto_eleitoral": "Eleitores insatisfeitos com falta de atendimento"}
            for b in criticos[:3]
        ],
        "oportunidades": [
            {"bairro": b["bairro"], "acao_sugerida": "Divulgar taxa de resolução alta", "justificativa": f"{b['taxa_resolucao']}% das demandas resolvidas — capital político a explorar"}
            for b in oportunidades[:3]
        ],
        "ranking_prioridade": [b["bairro"] for b in bairros[:5]],
        "alerta": f"Configure a ANTHROPIC_API_KEY para análise eleitoral completa com IA.",
    }


def _simular_com_regras(bairro: str, acao: str, bairro_dados: dict, totais: dict) -> dict:
    taxa = bairro_dados.get("taxa_resolucao", 0)
    total = bairro_dados.get("total_demandas", 0)
    impacto = "alto" if total > 20 else "medio" if total > 5 else "baixo"

    return {
        "impacto_estimado": impacto,
        "votos_potenciais": f"Estimativa indisponível sem IA. O bairro tem {total} demandas registradas.",
        "prazo_efeito": "curto_prazo",
        "riscos": ["Análise limitada sem IA configurada"],
        "acoes_complementares": ["Configure a ANTHROPIC_API_KEY para simulações detalhadas"],
        "narrativa": f"O bairro {bairro} possui {total} demandas com taxa de resolução de {taxa}%. Ative a IA para simulação completa.",
    }
