"""
Agente de simulação sem API. Segue o mesmo roteiro do bot real usando uma
máquina de estados simples baseada no histórico de mensagens.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InteracaoBot
from sqlalchemy import select
from app.models import Cidadao

# Passos do roteiro em ordem
_PASSOS = [
    "consent",
    "nome",
    "localizacao",
    "descricao",
    "confirmacao",
]


@dataclass
class ResultadoMock:
    resposta_texto: str
    dados_demanda: Optional[dict] = None


async def processar_mock(
    wa_id: str,
    mensagem_cidadao: str,
    db: AsyncSession,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> ResultadoMock:
    historico = await _carregar_historico(wa_id, db)
    n_bot = sum(1 for h in historico if h.remetente == "bot")
    texto = mensagem_cidadao.strip().lower()

    # ── Passo 0: primeiro contato → pede consentimento ────────────────────────
    if n_bot == 0:
        return ResultadoMock(
            "Olá! 👋 Sou o assistente do gabinete.\n\n"
            "Vou te ajudar a registrar um pedido ou problema da sua região. "
            "Seus dados serão usados apenas para dar andamento à solicitação.\n\n"
            "Tudo bem? Responda *sim* ou *não*."
        )

    # ── Passo 1: aguardando consentimento ─────────────────────────────────────
    if n_bot == 1:
        if any(p in texto for p in ["sim", "s", "ok", "pode", "aceito", "concordo"]):
            return ResultadoMock("Ótimo! 😊 Qual é o seu *nome completo*?")
        else:
            return ResultadoMock(
                "Tudo bem, entendo. Se mudar de ideia é só mandar uma mensagem. "
                "Até mais! 👋"
            )

    # ── Passo 2: aguardando nome ──────────────────────────────────────────────
    if n_bot == 2:
        return ResultadoMock(
            f"Prazer, {mensagem_cidadao.strip().title()}! 📍\n\n"
            "Agora me fala *onde você mora*: pode compartilhar sua localização "
            "(📎 → Localização) ou digitar seu endereço/bairro."
        )

    # ── Passo 3: aguardando localização ───────────────────────────────────────
    if n_bot == 3:
        if latitude is not None and longitude is not None:
            return ResultadoMock(
                "Localização recebida! 📌\n\nAgora me conta: *qual é o problema ou pedido?* "
                "Descreva com o máximo de detalhes que puder."
            )
        else:
            return ResultadoMock(
                "Anotei! 📝\n\nAgora me conta: *qual é o problema ou pedido?* "
                "Descreva com o máximo de detalhes que puder."
            )

    # ── Passo 4: aguardando descrição → registra ──────────────────────────────
    if n_bot == 4:
        # Extrai dados do histórico
        nome = _extrair_resposta(historico, passo_bot=2)
        localizacao = _extrair_resposta(historico, passo_bot=3)
        descricao = mensagem_cidadao.strip()

        dados = {
            "nome": nome.title() if nome else "Não informado",
            "endereco_texto": localizacao if not (latitude or longitude) else None,
            "latitude": latitude,
            "longitude": longitude,
            "descricao": descricao,
            "categoria": _inferir_categoria(descricao),
            "resumo": descricao[:60] + ("…" if len(descricao) > 60 else ""),
        }

        return ResultadoMock(
            f"Prontinho! ✅ Registrei sua solicitação sobre:\n"
            f"_{dados['resumo']}_\n\n"
            "O assessor da sua região vai dar retorno em breve. "
            "Obrigado por entrar em contato! 🙏",
            dados_demanda=dados,
        )

    # ── Após registro: mensagem extra ─────────────────────────────────────────
    return ResultadoMock(
        "Sua solicitação já foi registrada! 😊 "
        "Se quiser abrir uma nova, é só mandar *oi* novamente."
    )


def _extrair_resposta(historico: list, passo_bot: int) -> str:
    """Pega a mensagem do cidadão que veio logo após a N-ésima fala do bot."""
    falas_bot = 0
    for i, h in enumerate(historico):
        if h.remetente == "bot":
            falas_bot += 1
        if falas_bot == passo_bot and h.remetente == "bot":
            # próxima mensagem do cidadão
            for j in range(i + 1, len(historico)):
                if historico[j].remetente == "cidadao":
                    return historico[j].mensagem
    return ""


def _inferir_categoria(descricao: str) -> str:
    """Classificação simples por palavras-chave enquanto o Claude não está ativo."""
    d = descricao.lower()
    if any(p in d for p in ["buraco", "asfalto", "calçada", "esgoto", "obra"]):
        return "infraestrutura"
    if any(p in d for p in ["luz", "poste", "iluminação", "escuro"]):
        return "iluminacao"
    if any(p in d for p in ["saúde", "posto", "médico", "hospital", "ubs"]):
        return "saude"
    if any(p in d for p in ["escola", "creche", "educação", "professor"]):
        return "educacao"
    if any(p in d for p in ["ônibus", "transporte", "linha", "ponto"]):
        return "transporte"
    if any(p in d for p in ["segurança", "violência", "crime", "roubo"]):
        return "seguranca"
    if any(p in d for p in ["lixo", "entulho", "árvore", "ambiente"]):
        return "meio_ambiente"
    return "outro"


async def _carregar_historico(wa_id: str, db: AsyncSession) -> list[InteracaoBot]:
    result = await db.execute(select(Cidadao).where(Cidadao.wa_id == wa_id))
    cidadao = result.scalar_one_or_none()
    if not cidadao:
        return []
    result = await db.execute(
        select(InteracaoBot)
        .where(InteracaoBot.cidadao_id == cidadao.id)
        .order_by(InteracaoBot.timestamp)
    )
    return list(result.scalars().all())
