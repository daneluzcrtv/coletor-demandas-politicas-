"""
Cadastra os bairros reais de Itapecerica da Serra via API.
Uso: python3 seed_bairros.py
Coordenadas coletadas a partir do centro da cidade (-23.7170, -46.8430).
"""

import httpx

BASE = "http://localhost:8000"

# (nome, zona, lat_centro, lon_centro)
BAIRROS = [
    # ── Central ──────────────────────────────────────────────────────────
    ("Centro",                          "Central", -23.7140, -46.8490),
    ("Jardim Itapecerica",              "Central", -23.7100, -46.8430),
    ("Jardim Tereza Maria",             "Central", -23.7160, -46.8450),
    ("Olaria",                          "Central", -23.7200, -46.8480),
    ("Vila Cruzeiro",                   "Central", -23.7230, -46.8440),

    # ── Norte ─────────────────────────────────────────────────────────────
    ("Jardim Montesano",                "Norte",   -23.7020, -46.8470),
    ("Parque Paraíso",                  "Norte",   -23.6900, -46.8760),
    ("Jardim São Marcos",               "Norte",   -23.7050, -46.8580),
    ("Jardim Calux",                    "Norte",   -23.7040, -46.8535),
    ("Itaquaciara",                     "Norte",   -23.6950, -46.8650),
    ("Parque dos Pássaros",             "Norte",   -23.7010, -46.8650),
    ("Parque Residencial Júlio Corrêa", "Norte",   -23.6910, -46.8440),
    ("Jardim Eliza",                    "Norte",   -23.6960, -46.8510),
    ("Jardim Branca Flor",              "Norte",   -23.7050, -46.8350),
    ("Parque Santa Fé",                 "Norte",   -23.7050, -46.8380),
    ("Jardim Caguassu",                 "Norte",   -23.6970, -46.8660),

    # ── Sul ───────────────────────────────────────────────────────────────
    ("Lagoa",                           "Sul",     -23.7450, -46.8700),
    ("Valo Velho",                      "Sul",     -23.7380, -46.8540),
    ("Ressaca",                         "Sul",     -23.7520, -46.8350),
    ("Potuvera",                        "Sul",     -23.7500, -46.8200),
    ("Recanto das Flores",              "Sul",     -23.7470, -46.8640),
    ("Estância São Paulo",              "Sul",     -23.7420, -46.8550),
    ("Engenho Velho",                   "Sul",     -23.7500, -46.8380),
    ("Jardim São Luís",                 "Sul",     -23.7340, -46.8460),
    ("Mombaca",                         "Sul",     -23.7400, -46.8300),
    ("Jardim Nisalves",                 "Sul",     -23.7350, -46.8300),
    ("Jardim Marilu",                   "Sul",     -23.7310, -46.8390),

    # ── Oeste ─────────────────────────────────────────────────────────────
    ("Jardim Embu Mirim",               "Oeste",   -23.7000, -46.8800),
    ("Jardim Santa Isabel",             "Oeste",   -23.7200, -46.8600),
    ("Jardim Jacira",                   "Oeste",   -23.7300, -46.8700),
    ("Horizonte Azul",                  "Oeste",   -23.7200, -46.8800),
    ("Jardim Cinira",                   "Oeste",   -23.7150, -46.8700),
    ("Chácara Alvorada",                "Oeste",   -23.7140, -46.8740),
    ("Vila Olinda",                     "Oeste",   -23.7230, -46.8680),
    ("Jardim Itapevi",                  "Oeste",   -23.7310, -46.8790),
    ("Jardim Santa Júlia",              "Oeste",   -23.7180, -46.8750),
    ("Jardim Idemori",                  "Oeste",   -23.7260, -46.8750),

    # ── Leste ─────────────────────────────────────────────────────────────
    ("Jardim Niterói",                  "Leste",   -23.7190, -46.8220),
    ("Jardim América",                  "Leste",   -23.7130, -46.8140),
    ("Jardim Monte Alegre",             "Leste",   -23.7100, -46.8300),
    ("Jardim São Pedro",                "Leste",   -23.7200, -46.8350),
    ("Jardim Paraíso",                  "Leste",   -23.7050, -46.8350),
    ("Vila Rica",                       "Leste",   -23.7170, -46.8560),
    ("Recanto Floresta",                "Leste",   -23.7150, -46.8150),

    # ── Rural ─────────────────────────────────────────────────────────────
    ("Chácara Santa Maria",             "Rural",   -23.7350, -46.8600),
    ("Jardim Valo Velho",               "Rural",   -23.7420, -46.8480),
]


def main():
    client = httpx.Client(timeout=30)

    print("🔐 Autenticando...")
    r = client.post(f"{BASE}/auth/login", json={"email": "deputado@gabinete.com", "senha": "demo123"})
    r.raise_for_status()
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    print("   OK")

    print("\n📍 Buscando bairros existentes...")
    existentes = {b["nome"] for b in client.get(f"{BASE}/bairros/", headers=h).json()}
    print(f"   {len(existentes)} já cadastrados")

    criados = 0
    ja_existiam = 0
    for nome, zona, lat, lon in BAIRROS:
        if nome in existentes:
            ja_existiam += 1
            print(f"   · {nome} (já existe)")
            continue

        payload = {"nome": nome, "zona": zona}
        r = client.post(f"{BASE}/bairros/", headers=h, json=payload)
        if r.is_success:
            criados += 1
            print(f"   ✓ {nome} [{zona}]")
        else:
            print(f"   ✗ {nome}: {r.text[:80]}")

    print(f"\n✅ Concluído: {criados} criados, {ja_existiam} já existiam. Total: {len(BAIRROS)} bairros.")
    client.close()


if __name__ == "__main__":
    main()
