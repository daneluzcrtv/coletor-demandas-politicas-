from typing import Optional

import httpx

from app.config import settings

_NOMINATIM = "https://nominatim.openstreetmap.org"
_HEADERS = {"User-Agent": settings.nominatim_user_agent}


async def geocodificar(endereco: str) -> Optional[tuple[float, float]]:
    """Converte endereço em texto para (latitude, longitude). Retorna None se não encontrar."""
    params = {"q": endereco, "format": "json", "limit": 1}
    async with httpx.AsyncClient(headers=_HEADERS) as client:
        r = await client.get(f"{_NOMINATIM}/search", params=params, timeout=10)
        r.raise_for_status()
        resultados = r.json()

    if not resultados:
        return None

    return float(resultados[0]["lat"]), float(resultados[0]["lon"])


async def geocodificacao_reversa(lat: float, lon: float) -> Optional[str]:
    """
    Converte coordenadas em nome de bairro/subdistrito.
    Retorna o campo 'suburb' ou 'neighbourhood' do Nominatim, que costuma ser o bairro.
    """
    params = {"lat": lat, "lon": lon, "format": "json"}
    async with httpx.AsyncClient(headers=_HEADERS) as client:
        r = await client.get(f"{_NOMINATIM}/reverse", params=params, timeout=10)
        r.raise_for_status()
        dados = r.json()

    endereco = dados.get("address", {})
    # Nominatim retorna campos diferentes dependendo da região — tentamos em ordem de precisão
    return (
        endereco.get("suburb")
        or endereco.get("neighbourhood")
        or endereco.get("city_district")
        or endereco.get("town")
        or endereco.get("village")
    )
