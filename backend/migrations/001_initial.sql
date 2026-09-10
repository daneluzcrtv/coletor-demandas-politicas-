-- Habilita extensão PostGIS (requer PostgreSQL + PostGIS instalados)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabela assessor (criada antes de bairro por causa da FK)
CREATE TABLE IF NOT EXISTS assessor (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    areas_tematicas TEXT[],
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela bairro
CREATE TABLE IF NOT EXISTS bairro (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    zona TEXT,
    poligono GEOMETRY(POLYGON, 4326),
    assessor_responsavel_id INTEGER REFERENCES assessor(id)
);

-- Tabela cidadao
CREATE TABLE IF NOT EXISTS cidadao (
    id SERIAL PRIMARY KEY,
    wa_id TEXT UNIQUE,               -- número WhatsApp do cidadão (ex: "5511999999999")
    nome TEXT NOT NULL,
    telefone TEXT,
    endereco_texto TEXT,
    bairro_id INTEGER REFERENCES bairro(id),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    total_demandas INTEGER DEFAULT 0,
    data_cadastro TIMESTAMP DEFAULT NOW()
);

-- Tabela demanda
CREATE TABLE IF NOT EXISTS demanda (
    id SERIAL PRIMARY KEY,
    cidadao_id INTEGER REFERENCES cidadao(id),
    descricao TEXT NOT NULL,
    categoria TEXT,
    resumo TEXT,
    bairro_id INTEGER REFERENCES bairro(id),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status TEXT DEFAULT 'aberta',
    assessor_responsavel_id INTEGER REFERENCES assessor(id),
    canal_origem TEXT DEFAULT 'whatsapp',
    protocolo TEXT UNIQUE,
    data_abertura TIMESTAMP DEFAULT NOW(),
    data_conclusao TIMESTAMP
);

-- Tabela interacao_bot
CREATE TABLE IF NOT EXISTS interacao_bot (
    id SERIAL PRIMARY KEY,
    cidadao_id INTEGER REFERENCES cidadao(id),
    mensagem TEXT,
    remetente TEXT,          -- 'cidadao' | 'bot'
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Índices úteis
CREATE INDEX IF NOT EXISTS idx_demanda_status ON demanda(status);
CREATE INDEX IF NOT EXISTS idx_demanda_bairro ON demanda(bairro_id);
CREATE INDEX IF NOT EXISTS idx_demanda_assessor ON demanda(assessor_responsavel_id);
CREATE INDEX IF NOT EXISTS idx_demanda_data ON demanda(data_abertura);
CREATE INDEX IF NOT EXISTS idx_cidadao_wa_id ON cidadao(wa_id);
