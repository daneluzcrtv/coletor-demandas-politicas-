import math
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assessor, Bairro
from app.services.geocoding import geocodificacao_reversa

# Centroides calculados a partir das coordenadas reais das demandas no banco.
# Usados como fallback quando PostGIS e Nominatim não encontram o bairro.
_CENTROIDES: dict[str, tuple[float, float]] = {
    "Centro":                          (-23.71414, -46.84924),
    "Parque Paraíso":                  (-23.68987, -46.87483),
    "Jardim Calux":                    (-23.70279, -46.85218),
    "Estância São Paulo":              (-23.74186, -46.85581),
    "Vila Cruzeiro":                   (-23.72391, -46.84368),
    "Parque Santa Fé":                 (-23.70757, -46.83908),
    "Jardim São Luís":                 (-23.73536, -46.84608),
    "Vila Rica":                       (-23.71743, -46.85636),
    "Jardim Monte Alegre":             (-23.71197, -46.82987),
    "Engenho Velho":                   (-23.75027, -46.83778),
    "Parque dos Pássaros":             (-23.69879, -46.86263),
    "Chácara Alvorada":                (-23.71434, -46.87366),
    "Jardim Niterói":                  (-23.71865, -46.81949),
    "Recanto das Flores":              (-23.74636, -46.86200),
    "Jardim Caguassu":                 (-23.69468, -46.86815),
    "Vila Olinda":                     (-23.72133, -46.87199),
    "Jardim Itapevi":                  (-23.72741, -46.87563),
    "Jardim América":                  (-23.70980, -46.81394),
    "Jardim Itapecerica":              (-23.7100,  -46.8430),
    "Jardim Tereza Maria":             (-23.7160,  -46.8450),
    "Olaria":                          (-23.7200,  -46.8480),
    "Jardim Montesano":                (-23.7020,  -46.8470),
    "Jardim São Marcos":               (-23.7050,  -46.8580),
    "Itaquaciara":                     (-23.6950,  -46.8650),
    "Parque Residencial Júlio Corrêa": (-23.6910,  -46.8440),
    "Jardim Eliza":                    (-23.6960,  -46.8510),
    "Jardim Branca Flor":              (-23.7050,  -46.8350),
    "Jardim São Pedro":                (-23.7200,  -46.8350),
    "Jardim Paraíso":                  (-23.7050,  -46.8350),
    "Lagoa":                           (-23.7450,  -46.8700),
    "Valo Velho":                      (-23.7380,  -46.8540),
    "Ressaca":                         (-23.7520,  -46.8350),
    "Potuvera":                        (-23.7500,  -46.8200),
    "Mombaca":                         (-23.7400,  -46.8300),
    "Jardim Nisalves":                 (-23.7350,  -46.8300),
    "Jardim Marilu":                   (-23.7310,  -46.8390),
    "Jardim Embu Mirim":               (-23.7000,  -46.8800),
    "Jardim Santa Isabel":             (-23.7200,  -46.8600),
    "Jardim Jacira":                   (-23.7300,  -46.8700),
    "Horizonte Azul":                  (-23.7200,  -46.8800),
    "Jardim Cinira":                   (-23.7150,  -46.8700),
    "Jardim Santa Júlia":              (-23.7180,  -46.8750),
    "Jardim Idemori":                  (-23.7260,  -46.8750),
    "Recanto Floresta":                (-23.7150,  -46.8150),
    "Chácara Santa Maria":             (-23.7350,  -46.8600),
    "Jardim Valo Velho":               (-23.7420,  -46.8480),
}

_LIMIAR_KM = 2.5  # ignora bairros mais distantes que isso


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def encontrar_bairro(
    lat: float,
    lon: float,
    db: AsyncSession,
) -> Optional[Bairro]:
    """
    Tenta achar o bairro em três etapas:
    1. PostGIS: verifica se o ponto está dentro de algum polígono cadastrado.
    2. Nominatim: geocodificação reversa + match por nome no banco.
    3. Centroide mais próximo: Haversine contra coordenadas conhecidas dos bairros.
    """
    # Etapa 1 — PostGIS
    try:
        async with db.begin_nested():
            resultado = await db.execute(
                text(
                    "SELECT id FROM bairro "
                    "WHERE poligono IS NOT NULL "
                    "AND ST_Contains(poligono, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))"
                ),
                {"lat": lat, "lon": lon},
            )
            row = resultado.first()
            if row:
                return await db.get(Bairro, row[0])
    except Exception:
        pass

    # Etapa 2 — Nominatim + match textual
    nome_bairro = await geocodificacao_reversa(lat, lon)
    if nome_bairro:
        resultado = await db.execute(
            select(Bairro).where(Bairro.nome.ilike(f"%{nome_bairro}%"))
        )
        bairro = resultado.scalar_one_or_none()
        if bairro:
            return bairro

    # Etapa 3 — centroide mais próximo
    todos = (await db.execute(select(Bairro))).scalars().all()
    nome_para_bairro = {b.nome: b for b in todos}

    melhor_bairro: Optional[Bairro] = None
    melhor_dist = _LIMIAR_KM

    for nome, (clat, clon) in _CENTROIDES.items():
        dist = _haversine_km(lat, lon, clat, clon)
        if dist < melhor_dist:
            bairro_obj = nome_para_bairro.get(nome)
            if bairro_obj:
                melhor_dist = dist
                melhor_bairro = bairro_obj

    return melhor_bairro


async def encontrar_assessor(
    bairro: Bairro,
    categoria: Optional[str],
    db: AsyncSession,
) -> Optional[Assessor]:
    """
    Retorna o assessor responsável pelo bairro.
    Se a categoria bater com as áreas temáticas de outro assessor ativo, prefere esse.
    """
    if not bairro.assessor_responsavel_id:
        return None

    assessor_bairro = await db.get(Assessor, bairro.assessor_responsavel_id)

    # Se não temos categoria ou o assessor do bairro já cobre, retorna direto
    if not categoria or not assessor_bairro:
        return assessor_bairro

    if assessor_bairro.areas_tematicas and categoria in assessor_bairro.areas_tematicas:
        return assessor_bairro

    # Tenta achar assessor ativo com essa área temática
    resultado = await db.execute(
        select(Assessor).where(
            Assessor.ativo == True,
            Assessor.areas_tematicas.contains([categoria]),
        )
    )
    assessor_especialista = resultado.scalar_one_or_none()

    # Prefere especialista, mas usa o do bairro como fallback
    return assessor_especialista or assessor_bairro
