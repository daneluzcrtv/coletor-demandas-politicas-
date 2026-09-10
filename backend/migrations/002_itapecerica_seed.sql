-- Bairros de Itapecerica da Serra com coordenadas aproximadas dos centros
-- Fonte: conhecimento geográfico da cidade (polígonos podem ser adicionados depois)

INSERT INTO bairro (nome, zona) VALUES
    ('Centro',                  'Central'),
    ('Jardim Calux',            'Norte'),
    ('Parque Santa Fé',         'Norte'),
    ('Jardim Caguassu',         'Norte'),
    ('Parque Paraíso',          'Norte'),
    ('Vila Cruzeiro',           'Central'),
    ('Chácara Alvorada',        'Oeste'),
    ('Estância São Paulo',      'Sul'),
    ('Jardim Monte Alegre',     'Leste'),
    ('Engenho Velho',           'Sul'),
    ('Jardim São Luís',         'Sul'),
    ('Vila Olinda',             'Oeste'),
    ('Jardim Niterói',          'Leste'),
    ('Parque dos Pássaros',     'Norte'),
    ('Jardim Itapevi',          'Oeste'),
    ('Vila Rica',               'Central'),
    ('Recanto das Flores',      'Sul'),
    ('Jardim América',          'Leste'),
    ('Parque Residencial Julio Corrêa', 'Norte'),
    ('Jardim Bela Vista',       'Oeste')
ON CONFLICT DO NOTHING;
