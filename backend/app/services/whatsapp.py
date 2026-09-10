import httpx

from app.config import settings

_BASE_URL = "https://graph.facebook.com/v19.0"


async def send_text(wa_id: str, texto: str) -> None:
    """Envia uma mensagem de texto para um número WhatsApp via Meta Cloud API."""
    url = f"{_BASE_URL}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "text",
        "text": {"body": texto},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
