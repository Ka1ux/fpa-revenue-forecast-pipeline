CREATE TABLE IF NOT EXISTS dim_tempo (
    data_id     SERIAL PRIMARY KEY,
    data        DATE UNIQUE NOT NULL,
    ano         INT NOT NULL,
    trimestre   INT NOT NULL,
    mes         INT NOT NULL,
    nome_mes    TEXT NOT NULL,
    dia_util    BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_produto (
    produto_id  SERIAL PRIMARY KEY,
    nome        TEXT NOT NULL,
    categoria   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_cliente (
    cliente_id  SERIAL PRIMARY KEY,
    nome        TEXT NOT NULL,
    segmento    TEXT NOT NULL,
    regiao      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_categoria_despesa (
    categoria_id SERIAL PRIMARY KEY,
    nome         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_vendas (
    venda_id    SERIAL PRIMARY KEY,
    data_id     INT REFERENCES dim_tempo(data_id),
    produto_id  INT REFERENCES dim_produto(produto_id),
    cliente_id  INT REFERENCES dim_cliente(cliente_id),
    receita     NUMERIC(12,2) NOT NULL,
    quantidade  INT NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_despesas (
    despesa_id   SERIAL PRIMARY KEY,
    data_id      INT REFERENCES dim_tempo(data_id),
    categoria_id INT REFERENCES dim_categoria_despesa(categoria_id),
    valor        NUMERIC(12,2) NOT NULL
);
