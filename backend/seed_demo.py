"""
Seed de dados para demonstração — insere 80 demandas realistas em Itapecerica da Serra.
Uso: python3 seed_demo.py
"""

import httpx
import random
import time

BASE = "http://localhost:8000"

# ── Geometria dos bairros reais de Itapecerica da Serra (lat/lon do centro) ──
BAIRROS_GEO = {
    # Central
    "Centro":                          (-23.7140, -46.8490),
    "Jardim Itapecerica":              (-23.7100, -46.8430),
    "Jardim Tereza Maria":             (-23.7160, -46.8450),
    "Olaria":                          (-23.7200, -46.8480),
    "Vila Cruzeiro":                   (-23.7230, -46.8440),
    # Norte
    "Jardim Montesano":                (-23.7020, -46.8470),
    "Parque Paraíso":                  (-23.6900, -46.8760),
    "Jardim São Marcos":               (-23.7050, -46.8580),
    "Jardim Calux":                    (-23.7040, -46.8535),
    "Itaquaciara":                     (-23.6950, -46.8650),
    "Parque dos Pássaros":             (-23.7010, -46.8650),
    "Parque Residencial Júlio Corrêa": (-23.6910, -46.8440),
    "Jardim Eliza":                    (-23.6960, -46.8510),
    "Jardim Branca Flor":              (-23.7050, -46.8350),
    "Parque Santa Fé":                 (-23.7050, -46.8380),
    "Jardim Caguassu":                 (-23.6970, -46.8660),
    # Sul
    "Lagoa":                           (-23.7450, -46.8700),
    "Valo Velho":                      (-23.7380, -46.8540),
    "Ressaca":                         (-23.7520, -46.8350),
    "Potuvera":                        (-23.7500, -46.8200),
    "Recanto das Flores":              (-23.7470, -46.8640),
    "Estância São Paulo":              (-23.7420, -46.8550),
    "Engenho Velho":                   (-23.7500, -46.8380),
    "Jardim São Luís":                 (-23.7340, -46.8460),
    "Mombaca":                         (-23.7400, -46.8300),
    "Jardim Nisalves":                 (-23.7350, -46.8300),
    "Jardim Marilu":                   (-23.7310, -46.8390),
    # Oeste
    "Jardim Embu Mirim":               (-23.7000, -46.8800),
    "Jardim Santa Isabel":             (-23.7200, -46.8600),
    "Jardim Jacira":                   (-23.7300, -46.8700),
    "Horizonte Azul":                  (-23.7200, -46.8800),
    "Chácara Alvorada":                (-23.7140, -46.8740),
    "Vila Olinda":                     (-23.7230, -46.8680),
    "Jardim Itapevi":                  (-23.7310, -46.8790),
    # Leste
    "Jardim Niterói":                  (-23.7190, -46.8220),
    "Jardim América":                  (-23.7130, -46.8140),
    "Jardim Monte Alegre":             (-23.7100, -46.8300),
    "Jardim São Pedro":                (-23.7200, -46.8350),
    "Vila Rica":                       (-23.7170, -46.8560),
    "Recanto Floresta":                (-23.7150, -46.8150),
}

# ── Templates de demandas por categoria ───────────────────────────────────────
DEMANDAS = {
    "infraestrutura": [
        ("Buraco enorme na Rua das Palmeiras, próximo ao número 342. Já causou queda de moto e precisa de reparo urgente antes de causar acidente grave.", "Buraco perigoso na Rua das Palmeiras"),
        ("Calçada completamente destruída na frente da escola municipal. Crianças e idosos em risco ao tentar passar pelo trecho.", "Calçada destruída em frente à escola"),
        ("Esgoto estourado há mais de 15 dias na Rua São José. Cheiro insuportável e risco de contaminação da água da chuva.", "Esgoto estourado na Rua São José há 2 semanas"),
        ("Cratera no meio da Avenida Principal desviando o trânsito há semanas. Risco sério de acidentes noturnos com quem não conhece a via.", "Cratera na avenida principal — trânsito desviado"),
        ("Galeria de água entupida causa alagamento toda vez que chove. Rua fica intransitável por horas impedindo saída dos moradores.", "Galeria entupida — alagamento recorrente"),
        ("Muro de arrimo cedeu na encosta da Rua da Esperança. Risco de deslizamento em época de chuva, duas famílias em área de risco.", "Muro de arrimo cedeu — risco de deslizamento"),
        ("Tampão de bueiro faltando no meio da rua perto da praça. Já provocou queda de ciclista na semana passada.", "Tampão de bueiro faltando — ciclista já caiu"),
        ("Asfalto ondulado na subida da Rua XV compromete suspensão dos carros. Moradores reclamam há meses sem retorno.", "Asfalto danificado na Rua XV — reclamação sem retorno"),
        ("Trecho de calçada sem acessibilidade próximo à UBS. Cadeirantes precisam usar a rua para passar, arriscando a vida.", "Calçada sem acessibilidade próximo à UBS"),
        ("Obra de pavimentação abandonada há 6 semanas deixou rua de terra. Poeira causa problemas respiratórios nos moradores.", "Obra de pavimentação abandonada — rua de terra"),
    ],
    "iluminacao": [
        ("Poste de luz apagado há 3 semanas na esquina da Rua Flores com a Av. Brasil. Noites perigosas para pedestres que voltam do trabalho.", "Poste apagado há 3 semanas — risco noturno"),
        ("Trecho de 200m sem iluminação pública na Rua Nova. Assaltos já aconteceram nesse ponto completamente às escuras.", "Trecho sem luz — assaltos acontecendo"),
        ("Lâmpada piscando no poste da praça central. Ambiente degradado e sem condição de uso no período noturno.", "Lâmpada piscando na praça — ambiente inseguro"),
        ("Cinco postes apagados consecutivos na Rua das Acácias. Área completamente às escuras após as 19h.", "Cinco postes apagados consecutivos"),
        ("Iluminação da quadra poliesportiva queimada há 1 mês. Jovens não conseguem usar o espaço à noite.", "Luz da quadra apagada — jovens sem espaço"),
        ("Poste inclinado na Rua do Cipó oferece risco de queda. Fios expostos à vista e ninguém da ENEL veio ainda.", "Poste inclinado com fios expostos"),
    ],
    "saude": [
        ("UBS do bairro está sem médico clínico geral há 2 meses. Moradores precisam ir até o centro para consulta básica, gastando R$15 de ônibus.", "UBS sem médico clínico há 2 meses"),
        ("Fila de espera para consulta no posto de saúde chega a 6 horas. Muitos idosos desistem e voltam sem atendimento.", "Fila de 6h no posto — idosos desistindo"),
        ("Falta de vacinas na UBS do bairro. Mães com bebês precisam ir ao centro para vacinar, enfrentando transporte lotado.", "Falta de vacinas na UBS local"),
        ("Unidade de saúde sem dentista há 4 meses. Moradores com dor de dente sem conseguir atendimento na rede pública.", "Posto sem dentista — moradores sem atendimento"),
        ("Remédios para hipertensão em falta na farmácia municipal. Pacientes com pressão alta sem medicação controlada.", "Falta de remédio para hipertensão"),
        ("Ambulância do SAMU demora mais de 1 hora para chegar ao bairro. Pedido de posto avançado de atendimento.", "SAMU demora 1h — pedido de posto avançado"),
    ],
    "educacao": [
        ("Telhado da escola municipal com goteira grave. Duas salas interditadas durante a chuva, 60 alunos sem aula.", "Telhado da escola com goteira — alunos sem aula"),
        ("Falta professor de matemática na escola estadual há 1 mês. Alunos do 9º ano sem aula da disciplina antes do ENEM.", "Escola sem professor de matemática"),
        ("Creche municipal com lista de espera de 80 crianças. Mães não conseguem trabalhar por falta de vaga.", "80 crianças na fila da creche"),
        ("Banheiros da escola sem água há uma semana. Condições insalubres afetam mais de 400 alunos.", "Escola sem água — condições insalubres"),
        ("Material didático não chegou para o 2º semestre. Alunos estudando sem livro há 3 semanas.", "Material didático não chegou ao 2º semestre"),
    ],
    "transporte": [
        ("Linha de ônibus 304 foi cortada sem aviso. Moradores ficaram sem transporte público para o trabalho no centro.", "Linha 304 cortada sem aviso prévio"),
        ("Ponto de ônibus sem cobertura. Passageiros ficam expostos à chuva esperando a condução às 5h da manhã.", "Ponto de ônibus sem cobertura — sem abrigo"),
        ("Ônibus superlotados no horário de pico. Motoristas passando sem parar por excesso de passageiros.", "Ônibus superlotados no pico"),
        ("Frequência do ônibus foi reduzida de 20 para 60 minutos. Trabalhadores chegam atrasados ao emprego e sofrem advertências.", "Frequência do ônibus caiu para 60 minutos"),
    ],
    "seguranca": [
        ("Série de assaltos na Rua do Comércio nas últimas duas semanas. Câmeras do bairro estão quebradas e sem manutenção.", "Assaltos recorrentes — câmeras quebradas"),
        ("Arrombamentos de carros aumentaram 3x no último mês. Rua sem policiamento visível há muito tempo.", "Arrombamentos triplicaram — sem policiamento"),
        ("Crimes favorecidos pela escuridão após 20h. Moradores pedem mais policiamento e iluminação urgente.", "Escuridão favorece crimes — pedido de policiamento"),
        ("Brigas e confusões frequentes próximo ao bar da esquina nos fins de semana. Famílias com medo.", "Brigas no bar — famílias com medo"),
    ],
    "meio_ambiente": [
        ("Descarte irregular de entulho na Rua do Cipó. Monte de lixo crescendo há semanas sem coleta pela prefeitura.", "Entulho irregular na Rua do Cipó"),
        ("Terreno baldio com mato alto virando foco de dengue. Já foram identificados criadouros de mosquito pelos moradores.", "Terreno com mato — foco de dengue"),
        ("Lixo acumulado nas margens do córrego aumenta risco de enchente. Coleta insuficiente na região.", "Lixo no córrego — risco de enchente"),
    ],
    "assistencia_social": [
        ("Família com 5 filhos em situação de vulnerabilidade sem acesso ao CRAS. Crianças sem cesta básica há meses.", "Família sem acesso ao CRAS"),
        ("Idosos sozinhos no bairro sem atendimento domiciliar. Pedido urgente de visita dos serviços sociais.", "Idosos isolados sem atendimento domiciliar"),
    ],
}

# ── Distribuição de demandas por bairro ───────────────────────────────────────
# (bairro, n_abertas, n_em_andamento, n_concluidas, categorias_principais)
DISTRIBUICAO = [
    # (bairro, n_abertas, n_em_andamento, n_concluidas, categorias_principais)
    ("Centro",                          4, 4, 4, ["infraestrutura", "iluminacao", "saude", "transporte"]),
    ("Parque Paraíso",                  6, 2, 2, ["infraestrutura", "iluminacao", "seguranca"]),
    ("Jardim Calux",                    3, 3, 1, ["infraestrutura", "educacao", "saude"]),
    ("Estância São Paulo",              2, 2, 3, ["infraestrutura", "transporte", "saude"]),
    ("Vila Cruzeiro",                   3, 2, 1, ["iluminacao", "seguranca", "infraestrutura"]),
    ("Parque Santa Fé",                 2, 1, 2, ["educacao", "saude", "infraestrutura"]),
    ("Jardim São Luís",                 3, 1, 1, ["infraestrutura", "meio_ambiente", "saude"]),
    ("Vila Rica",                       1, 2, 1, ["iluminacao", "transporte", "assistencia_social"]),
    ("Jardim Monte Alegre",             2, 1, 1, ["infraestrutura", "seguranca"]),
    ("Engenho Velho",                   2, 1, 0, ["meio_ambiente", "infraestrutura"]),
    ("Parque dos Pássaros",             1, 1, 1, ["iluminacao", "infraestrutura"]),
    ("Chácara Alvorada",                1, 2, 0, ["saude", "transporte"]),
    ("Jardim Niterói",                  1, 1, 0, ["seguranca", "infraestrutura"]),
    ("Recanto das Flores",              1, 0, 1, ["infraestrutura", "saude"]),
    ("Jardim Caguassu",                 2, 0, 0, ["infraestrutura", "educacao"]),
    ("Vila Olinda",                     0, 1, 0, ["meio_ambiente"]),
    ("Jardim Itapevi",                  0, 0, 1, ["infraestrutura"]),
    ("Jardim América",                  1, 0, 0, ["iluminacao"]),
    ("Parque Residencial Júlio Corrêa", 1, 0, 0, ["saude"]),
    ("Lagoa",                           2, 1, 0, ["infraestrutura", "meio_ambiente"]),
    ("Jardim Montesano",                1, 2, 1, ["infraestrutura", "transporte", "saude"]),
    ("Mombaca",                         1, 1, 0, ["seguranca", "iluminacao"]),
    ("Jardim Embu Mirim",               2, 0, 1, ["infraestrutura", "educacao"]),
    ("Valo Velho",                      1, 1, 0, ["infraestrutura", "saude"]),
    ("Itaquaciara",                     1, 0, 1, ["meio_ambiente", "infraestrutura"]),
]

# ── Nomes e dados dos cidadãos ────────────────────────────────────────────────
CIDADAOS = [
    ("Maria Silva",         "5511991110001", "Rua das Palmeiras, 342"),
    ("João Santos",         "5511991110002", "Av. Brasil, 1240"),
    ("Ana Oliveira",        "5511991110003", "Rua São José, 88"),
    ("Carlos Souza",        "5511991110004", "Rua das Flores, 55"),
    ("Fernanda Lima",       "5511991110005", "Rua Nova, 210"),
    ("Pedro Alves",         "5511991110006", "Av. Central, 330"),
    ("Lucia Ferreira",      "5511991110007", "Rua XV de Novembro, 74"),
    ("Roberto Costa",       "5511991110008", "Rua do Cipó, 19"),
    ("Mariana Gomes",       "5511991110009", "Rua Esperança, 107"),
    ("Paulo Rodrigues",     "5511991110010", "Rua das Acácias, 255"),
    ("Sandra Martins",      "5511991110011", "Rua do Comércio, 88"),
    ("Antonio Pereira",     "5511991110012", "Rua Alegria, 32"),
    ("Juliana Carvalho",    "5511991110013", "Rua das Rosas, 66"),
    ("Marcos Ribeiro",      "5511991110014", "Rua da Paz, 140"),
    ("Cristina Araújo",     "5511991110015", "Rua do Pinheiro, 77"),
    ("Felipe Barros",       "5511991110016", "Rua Boa Vista, 200"),
    ("Tatiana Mendes",      "5511991110017", "Rua das Violetas, 45"),
    ("Eduardo Nascimento",  "5511991110018", "Rua São Luís, 330"),
    ("Patricia Castro",     "5511991110019", "Rua América, 89"),
    ("Rodrigo Freitas",     "5511991110020", "Rua Julio Corrêa, 12"),
]

ACOMP_NOTAS = [
    ("nota",            "Demanda recebida e registrada. Aguardando análise da equipe técnica.", "Assessoria"),
    ("contato",         "Contactado o cidadão para confirmar o endereço exato do problema.", "Assessor"),
    ("visita",          "Visita técnica realizada ao local. Situação confirmada e fotografada.", "Assessoria Técnica"),
    ("encaminhamento",  "Demanda encaminhada ao setor responsável da Prefeitura. Aguardando retorno.", "Assessoria"),
    ("resolucao_parcial", "Manutenção parcial realizada. Equipe retorna em 5 dias para concluir.", "Assessoria Técnica"),
    ("nota",            "Reunião com secretaria para tratar o caso. Previsão de resolução em 10 dias.", "Assessor"),
]


def jitter(coord, r=0.004):
    return coord + random.uniform(-r, r)


def pick_demanda(cats):
    cat = random.choice(cats)
    templates = DEMANDAS.get(cat, DEMANDAS["infraestrutura"])
    desc, resumo = random.choice(templates)
    return cat, desc, resumo


def main():
    random.seed(42)
    client = httpx.Client(timeout=30)

    print("🔐 Autenticando...")
    r = client.post(f"{BASE}/auth/login", json={"email": "deputado@gabinete.com", "senha": "demo123"})
    r.raise_for_status()
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    print("   OK")

    # Bairros — criar os que faltam (bairros reais de Itapecerica da Serra)
    BAIRROS_SEED = [
        ("Centro",                          "Central"),
        ("Jardim Itapecerica",              "Central"),
        ("Jardim Tereza Maria",             "Central"),
        ("Olaria",                          "Central"),
        ("Vila Cruzeiro",                   "Central"),
        ("Jardim Montesano",                "Norte"),
        ("Parque Paraíso",                  "Norte"),
        ("Jardim São Marcos",               "Norte"),
        ("Jardim Calux",                    "Norte"),
        ("Itaquaciara",                     "Norte"),
        ("Parque dos Pássaros",             "Norte"),
        ("Parque Residencial Júlio Corrêa", "Norte"),
        ("Jardim Eliza",                    "Norte"),
        ("Jardim Branca Flor",              "Norte"),
        ("Parque Santa Fé",                 "Norte"),
        ("Jardim Caguassu",                 "Norte"),
        ("Lagoa",                           "Sul"),
        ("Valo Velho",                      "Sul"),
        ("Ressaca",                         "Sul"),
        ("Potuvera",                        "Sul"),
        ("Recanto das Flores",              "Sul"),
        ("Estância São Paulo",              "Sul"),
        ("Engenho Velho",                   "Sul"),
        ("Jardim São Luís",                 "Sul"),
        ("Mombaca",                         "Sul"),
        ("Jardim Nisalves",                 "Sul"),
        ("Jardim Marilu",                   "Sul"),
        ("Jardim Embu Mirim",               "Oeste"),
        ("Jardim Santa Isabel",             "Oeste"),
        ("Jardim Jacira",                   "Oeste"),
        ("Horizonte Azul",                  "Oeste"),
        ("Chácara Alvorada",                "Oeste"),
        ("Vila Olinda",                     "Oeste"),
        ("Jardim Itapevi",                  "Oeste"),
        ("Jardim Niterói",                  "Leste"),
        ("Jardim América",                  "Leste"),
        ("Jardim Monte Alegre",             "Leste"),
        ("Jardim São Pedro",                "Leste"),
        ("Vila Rica",                       "Leste"),
        ("Recanto Floresta",                "Leste"),
    ]
    bairros_raw = client.get(f"{BASE}/bairros/", headers=h).json()
    bairro_id = {b["nome"]: b["id"] for b in bairros_raw}
    print(f"   {len(bairro_id)} bairros já existem — criando os que faltam...")
    for nome, zona in BAIRROS_SEED:
        if nome not in bairro_id:
            r = client.post(f"{BASE}/bairros/", headers=h, json={"nome": nome, "zona": zona})
            if r.is_success:
                bairro_id[nome] = r.json()["id"]
                print(f"   + {nome}")
    print(f"   Total: {len(bairro_id)} bairros")

    # Assessores
    assessores_raw = client.get(f"{BASE}/assessores/", headers=h).json()
    assessor_ids = [a["id"] for a in assessores_raw]
    print(f"   {len(assessor_ids)} assessores encontrados")

    # Criar cidadãos
    print("\n👤 Criando cidadãos...")
    cidadao_ids = []
    for idx, (nome, wa_id, endereco) in enumerate(CIDADAOS):
        r = client.post(f"{BASE}/cidadaos/", headers=h, json={
            "nome": nome,
            "wa_id": wa_id,
            "telefone": wa_id,
            "endereco_texto": endereco,
        })
        if r.is_success:
            cidadao_ids.append(r.json()["id"])
            print(f"   ✓ {nome}")
        else:
            # Pode já existir
            cidadao_ids.append(None)
            print(f"   ! {nome} já existe ou erro: {r.text[:60]}")

    cidadao_ids_validos = [c for c in cidadao_ids if c]

    # Criar demandas
    print("\n📋 Criando demandas...")
    total_criadas = 0
    dem_template_idx = {cat: 0 for cat in DEMANDAS}

    for bairro_nome, n_abertas, n_em_andamento, n_concluidas, cats in DISTRIBUICAO:
        bid = bairro_id.get(bairro_nome)
        if not bid:
            print(f"   ⚠ Bairro '{bairro_nome}' não encontrado no banco — pulando")
            continue

        centro_lat, centro_lon = BAIRROS_GEO[bairro_nome]
        lote = (
            [("aberta", d) for d in range(n_abertas)] +
            [("em_andamento", d) for d in range(n_em_andamento)] +
            [("concluida", d) for d in range(n_concluidas)]
        )

        for status, _ in lote:
            cat, desc, resumo = pick_demanda(cats)
            lat = jitter(centro_lat)
            lon = jitter(centro_lon)
            cid = random.choice(cidadao_ids_validos) if cidadao_ids_validos else None
            aid = random.choice(assessor_ids) if assessor_ids else None

            # Criar demanda
            payload = {
                "descricao": desc,
                "bairro_id": bid,
                "latitude": lat,
                "longitude": lon,
                "canal_origem": "whatsapp",
            }
            if cid:
                payload["cidadao_id"] = cid

            r = client.post(f"{BASE}/demandas/", headers=h, json=payload)
            if not r.is_success:
                print(f"   ✗ Erro ao criar demanda: {r.text[:80]}")
                continue

            dem_id = r.json()["id"]

            # Atualizar categoria / resumo / status / assessor
            patch_data = {"categoria": cat, "resumo": resumo, "status": status}
            if aid:
                patch_data["assessor_responsavel_id"] = aid
            client.patch(f"{BASE}/demandas/{dem_id}", headers=h, json=patch_data)

            # Adicionar acompanhamento para demandas em andamento
            if status == "em_andamento":
                nota = random.choice(ACOMP_NOTAS)
                tipo, descricao_a, autor = nota
                client.post(
                    f"{BASE}/acompanhamento/demanda/{dem_id}",
                    headers=h,
                    data={"descricao": descricao_a, "tipo": tipo, "autor": autor},
                )

            # Adicionar acompanhamento de conclusão para concluídas
            if status == "concluida":
                client.post(
                    f"{BASE}/acompanhamento/demanda/{dem_id}",
                    headers=h,
                    data={
                        "descricao": "Problema resolvido com sucesso. Moradores notificados e situação normalizada.",
                        "tipo": "conclusao",
                        "autor": "Assessoria",
                    },
                )

            total_criadas += 1

        print(f"   ✓ {bairro_nome}: {n_abertas}a + {n_em_andamento}e + {n_concluidas}c")

    print(f"\n✅ Seed concluído! {total_criadas} demandas criadas em {len(DISTRIBUICAO)} bairros.")
    client.close()


if __name__ == "__main__":
    main()
