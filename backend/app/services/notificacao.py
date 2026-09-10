from __future__ import annotations

import re

from app.models import Assessor
from app.services.whatsapp import send_text


def normalizar_telefone(telefone: str) -> str | None:
    """Converte qualquer formato de telefone brasileiro para wa_id (ex: 5511999999999)."""
    if not telefone:
        return None
    digits = re.sub(r"\D", "", telefone)
    if not digits:
        return None
    if not digits.startswith("55"):
        digits = "55" + digits
    # 55 + DDD(2) + número(8 ou 9) = 12 ou 13 dígitos
    if len(digits) not in (12, 13):
        return None
    return digits


async def notificar_assessor_nova_demanda(
    assessor: Assessor,
    protocolo: str,
    nome_cidadao: str,
    bairro_nome: str | None,
    categoria: str | None,
    resumo: str | None,
) -> None:
    """Envia WhatsApp ao assessor informando nova demanda atribuída. Falhas são silenciadas."""
    wa_id = normalizar_telefone(assessor.telefone or "")
    if not wa_id:
        return

    linhas = [
        f"🔔 *Nova demanda atribuída — #{protocolo}*",
        "",
        f"👤 Cidadão: {nome_cidadao}",
        f"📍 Bairro: {bairro_nome or 'não identificado'}",
        f"🏷️ Categoria: {categoria or 'não categorizada'}",
    ]
    if resumo:
        linhas.append(f"📝 {resumo}")
    linhas += ["", "Acesse o painel para registrar o acompanhamento."]

    try:
        await send_text(wa_id, "\n".join(linhas))
    except Exception:
        pass
