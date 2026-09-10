"""
Importa polígonos aproximados de bairros via Nominatim (OpenStreetMap)
e salva na coluna 'poligono' da tabela bairro (PostGIS).

Uso: python3 importar_poligonos.py
"""

import asyncio
import sys
import unicodedata
import re

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

sys.path.insert(0, ".")
from app.config import settings

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
CIDADE = "Itapecerica da Serra, SP, Brasil"
HEADERS = {"User-Agent": "coletor-demandas-politicas/1.0"}


def bbox_para_wkt(bbox):
    """
    Converte bounding box [south, north, west, east] em WKT POLYGON.
    Reduz 20% para minimizar sobreposição entre bairros vizinhos.
    """
    s, n, w, e = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    lat_c = (s + n) / 2
    lon_c = (w + e) / 2
    f = 0.80
    s = lat_c + (s - lat_c) * f
    n = lat_c + (n - lat_c) * f
    w = lon_c + (w - lon_c) * f
    e = lon_c + (e - lon_c) * f
    return f"POLYGON(({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))", lat_c, lon_c


async def main():
    engine = create_async_engine(settings.database_url, echo=False)

    async with AsyncSession(engine) as db:
        # 1. Garante que a coluna poligono existe
        print("→ Verificando coluna poligono...")
        await db.execute(text(
            "ALTER TABLE bairro ADD COLUMN IF NOT EXISTS poligono geometry(Geometry, 4326)"
        ))
        await db.commit()
        print("  OK.")

        # 2. Carrega bairros
        r = await db.execute(text("SELECT id, nome FROM bairro ORDER BY nome"))
        bairros = {row[0]: row[1] for row in r.fetchall()}
        print(f"  {len(bairros)} bairros no banco.\n")

        # 3. Para cada bairro, busca bounding box no Nominatim
        print(f"→ Consultando Nominatim ({len(bairros)} bairros, 1 req/s)...\n")

        atualizados = []
        nao_encontrados = []

        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
            for bid, nome in bairros.items():
                await asyncio.sleep(1.1)

                try:
                    resp = await client.get(NOMINATIM_URL, params={
                        "q": f"{nome}, {CIDADE}",
                        "format": "json",
                        "limit": 3,
                        "addressdetails": 1,
                    })
                    resultados = resp.json()
                except Exception as e:
                    print(f"  ERRO rede — {nome}: {e}")
                    nao_encontrados.append(nome)
                    continue

                # Prefere resultados que mencionem Itapecerica da Serra no endereço
                resultado = None
                for res in resultados:
                    addr = res.get("address", {})
                    cidade_res = addr.get("city") or addr.get("town") or addr.get("municipality") or ""
                    if "itapecerica" in cidade_res.lower():
                        resultado = res
                        break
                if not resultado and resultados:
                    resultado = resultados[0]

                if not resultado or not resultado.get("boundingbox"):
                    print(f"  ✗ {nome}: não encontrado")
                    nao_encontrados.append(nome)
                    continue

                wkt, lat_c, lon_c = bbox_para_wkt(resultado["boundingbox"])

                await db.execute(
                    text("UPDATE bairro SET poligono = ST_GeomFromText(:wkt, 4326) WHERE id = :id"),
                    {"wkt": wkt, "id": bid},
                )
                atualizados.append(nome)
                print(f"  ✓ {nome}  (centro ~{lat_c:.4f}, {lon_c:.4f})")

        await db.commit()

        r2 = await db.execute(text("SELECT COUNT(*) FROM bairro WHERE poligono IS NOT NULL"))
        total = r2.scalar()

    await engine.dispose()

    print(f"\n{'='*50}")
    print(f"RESULTADO: {total}/{len(bairros)} bairros com polígono salvo")
    if nao_encontrados:
        print(f"\nNão encontrados ({len(nao_encontrados)}):")
        for n in nao_encontrados:
            print(f"  · {n}")


if __name__ == "__main__":
    asyncio.run(main())
