import json
import re
from dataclasses import dataclass
from typing import Optional

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import InteracaoBot

_CHAVE_VALIDA = (
    settings.anthropic_api_key.startswith("sk-ant-")
    and len(settings.anthropic_api_key) > 20
)
_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key) if _CHAVE_VALIDA else None

SYSTEM_PROMPT = """Você é o assistente virtual do gabinete do(a) vereador(a). \
Seu trabalho é registrar demandas e pedidos dos cidadãos de forma simpática e objetiva. \
Fale sempre em português brasileiro informal, mas respeitoso.

Siga este roteiro em ordem:
1. Apresente-se e peça consentimento para usar os dados (só para atendimento). \
   Se o cidadão recusar, encerre educadamente.
2. Pergunte o nome completo.
3. Peça a localização: "Você pode compartilhar sua localização pelo WhatsApp \
   (clipe 📎 → Localização) ou digitar seu endereço/bairro?"
4. Pergunte qual é o problema ou pedido, com detalhes.
5. Quando tiver nome + localização (texto ou coordenadas) + descrição da demanda, \
   confirme com o cidadão em uma frase curta e emita o bloco de registro abaixo. \
   NÃO emita o bloco antes de ter os três dados.

Formato do bloco de registro (coloque exatamente assim, em uma linha separada):
<REGISTRAR>{"nome": "...", "endereco_texto": "...", "latitude": null, "longitude": null, "descricao": "...", "categoria": "...", "resumo": "..."}</REGISTRAR>

Categorias válidas para o campo "categoria":
infraestrutura, saude, educacao, iluminacao, seguranca, transporte, meio_ambiente, assistencia_social, outro

O campo "resumo" deve ter no máximo 10 palavras descrevendo o pedido.

Regras:
- Se o cidadão compartilhar localização GPS, use as coordenadas e deixe endereco_texto como null.
- Se digitar endereço em texto, use endereco_texto e deixe latitude/longitude como null.
- Depois do bloco <REGISTRAR>, informe o número do protocolo que será gerado e diga que \
  o assessor da região vai entrar em contato.
- Se o cidadão mandar mensagem fora do contexto, redirecione gentilmente para o fluxo.
- Nunca invente dados. Se não souber algo, pergunte."""

_REGISTRAR_PATTERN = re.compile(r"<REGISTRAR>(.*?)</REGISTRAR>", re.DOTALL)


@dataclass
class ResultadoAgente:
    resposta_texto: str           # texto a enviar pro cidadão
    dados_demanda: Optional[dict] # preenchido quando Claude emitiu <REGISTRAR>


async def processar(
    wa_id: str,
    mensagem_cidadao: str,
    db: AsyncSession,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> ResultadoAgente:
    """
    Carrega histórico, chama Claude (ou mock) e retorna o que enviar ao cidadão.
    Usa mock automático se a ANTHROPIC_API_KEY não estiver configurada.
    """
    if not _CHAVE_VALIDA:
        from app.bot.mock_agente import processar_mock, ResultadoMock
        resultado = await processar_mock(wa_id, mensagem_cidadao, db, latitude, longitude)
        return ResultadoAgente(
            resposta_texto=resultado.resposta_texto,
            dados_demanda=resultado.dados_demanda,
        )

    # Monta texto de entrada — se vier localização GPS, descreve isso
    if latitude is not None and longitude is not None:
        mensagem_cidadao = (
            f"[Localização compartilhada] latitude={latitude}, longitude={longitude}"
        )

    historico = await _carregar_historico(wa_id, db)

    # Monta lista de mensagens no formato da API do Claude
    messages = []
    for interacao in historico:
        role = "user" if interacao.remetente == "cidadao" else "assistant"
        messages.append({"role": role, "content": interacao.mensagem})
    messages.append({"role": "user", "content": mensagem_cidadao})

    resposta = await _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    texto_resposta = resposta.content[0].text

    # Verifica se Claude emitiu um bloco <REGISTRAR>
    match = _REGISTRAR_PATTERN.search(texto_resposta)
    dados_demanda = None
    if match:
        try:
            dados_demanda = json.loads(match.group(1))
            dados_demanda["latitude"] = latitude if dados_demanda.get("latitude") is None else dados_demanda["latitude"]
            dados_demanda["longitude"] = longitude if dados_demanda.get("longitude") is None else dados_demanda["longitude"]
        except json.JSONDecodeError:
            pass  # bloco malformado — Claude vai corrigir na próxima rodada

        # Remove o bloco técnico do texto que o cidadão vai ver
        texto_resposta = _REGISTRAR_PATTERN.sub("", texto_resposta).strip()

    return ResultadoAgente(
        resposta_texto=texto_resposta,
        dados_demanda=dados_demanda,
    )


async def _carregar_historico(wa_id: str, db: AsyncSession) -> list[InteracaoBot]:
    """Retorna as últimas 20 interações do cidadão, em ordem cronológica."""
    from app.models import Cidadao

    result = await db.execute(
        select(Cidadao).where(Cidadao.wa_id == wa_id)
    )
    cidadao = result.scalar_one_or_none()
    if not cidadao:
        return []

    result = await db.execute(
        select(InteracaoBot)
        .where(InteracaoBot.cidadao_id == cidadao.id)
        .order_by(InteracaoBot.timestamp.desc())
        .limit(20)
    )
    interacoes = result.scalars().all()
    return list(reversed(interacoes))  # cronológico
