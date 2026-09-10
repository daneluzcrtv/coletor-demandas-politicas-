"""
Reatribui o bairro de todas as demandas com coordenadas GPS usando a lógica
de centroide mais próximo (mesma que o backend usa ao receber novas demandas).

Uso:
    cd backend
    python3 fix_bairros_demandas.py [--dry-run]

Flags:
    --dry-run   Mostra o que mudaria sem salvar no banco.
"""

import argparse
import math
import sys

import httpx

BASE = "http://localhost:8000"

# Centroides — espelho do que está em roteamento.py
CENTROIDES: dict[str, tuple[float, float]] = {
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

LIMIAR_KM = 2.5


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bairro_mais_proximo(lat, lon, nome_para_id):
    melhor_nome = None
    melhor_dist = LIMIAR_KM
    for nome, (clat, clon) in CENTROIDES.items():
        if nome not in nome_para_id:
            continue
        dist = haversine_km(lat, lon, clat, clon)
        if dist < melhor_dist:
            melhor_dist = dist
            melhor_nome = nome
    return melhor_nome, melhor_dist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Não salva, só mostra")
    args = parser.parse_args()

    client = httpx.Client(timeout=60)

    print("🔐 Autenticando...")
    r = client.post(f"{BASE}/auth/login", json={"email": "deputado@gabinete.com", "senha": "demo123"})
    r.raise_for_status()
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    print("   OK")

    print("\n📍 Carregando bairros...")
    bairros = client.get(f"{BASE}/bairros/", headers=h).json()
    nome_para_id = {b["nome"]: b["id"] for b in bairros}
    id_para_nome = {b["id"]: b["nome"] for b in bairros}
    print(f"   {len(bairros)} bairros carregados")

    print("\n📋 Carregando demandas...")
    demandas = []
    skip = 0
    limit = 100
    while True:
        page = client.get(f"{BASE}/demandas/", headers=h, params={"skip": skip, "limit": limit}).json()
        if not page:
            break
        demandas.extend(page)
        if len(page) < limit:
            break
        skip += limit
    print(f"   {len(demandas)} demandas carregadas")

    com_coords = [d for d in demandas if d.get("latitude") and d.get("longitude")]
    print(f"   {len(com_coords)} com coordenadas GPS\n")

    alteradas = 0
    sem_match = 0

    for d in com_coords:
        lat, lon = d["latitude"], d["longitude"]
        bairro_atual_id = d.get("bairro_id")
        bairro_atual_nome = id_para_nome.get(bairro_atual_id, "—") if bairro_atual_id else "—"

        novo_nome, dist = bairro_mais_proximo(lat, lon, nome_para_id)

        if not novo_nome:
            sem_match += 1
            print(f"   ⚠ #{d['protocolo']} ({lat:.5f},{lon:.5f}) — sem bairro dentro de {LIMIAR_KM}km")
            continue

        novo_id = nome_para_id[novo_nome]

        if novo_id == bairro_atual_id:
            continue  # já está correto

        alteradas += 1
        print(f"   {'[DRY]' if args.dry_run else '✓'} #{d['protocolo']} "
              f"{bairro_atual_nome!r} → {novo_nome!r} ({dist:.2f}km)")

        if not args.dry_run:
            patch = client.patch(
                f"{BASE}/demandas/{d['id']}",
                headers=h,
                json={"bairro_id": novo_id},
            )
            if not patch.is_success:
                print(f"      ✗ erro ao salvar: {patch.text[:120]}")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}✅ Concluído: "
          f"{alteradas} demandas {'seriam alteradas' if args.dry_run else 'alteradas'}, "
          f"{sem_match} sem match de bairro.")
    client.close()


if __name__ == "__main__":
    main()
