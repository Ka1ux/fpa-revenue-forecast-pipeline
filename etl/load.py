"""Loads cleaned data into Postgres following the star schema in sql/schema.sql."""
import os

import pandas as pd
from sqlalchemy import create_engine, text

CLEAN_DIR = "data/clean"
DB_URL = os.environ.get("FPA_DB_URL", "postgresql://fpa:fpa@localhost:5432/fpa")


def _limpar_fatos(engine) -> None:
    """Esvazia as tabelas fato para a carga ser idempotente (re-rodar não duplica)."""
    with engine.begin() as conn:
        for tabela in ("fato_vendas", "fato_despesas"):
            conn.execute(text(f"DELETE FROM {tabela}"))


def _chave(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    """Chave de comparação normalizada (datas viram 'YYYY-MM-DD' dos dois lados)."""
    out = frame[cols].copy()
    for c in cols:
        parsed = pd.to_datetime(out[c], errors="coerce")
        out[c] = parsed.dt.strftime("%Y-%m-%d") if parsed.notna().all() else out[c].astype(str)
    return out.apply(tuple, axis=1)


def _upsert_dim(engine, df: pd.DataFrame, table: str, cols: list[str]) -> pd.DataFrame:
    existentes = pd.read_sql(f"SELECT * FROM {table}", engine)
    novos = df[~_chave(df, cols).isin(_chave(existentes, cols))] if len(existentes) else df
    if len(novos):
        novos[cols].drop_duplicates().to_sql(table, engine, if_exists="append", index=False)
    return pd.read_sql(f"SELECT * FROM {table}", engine)


def carregar_dim_tempo(engine, calendario: pd.DataFrame) -> pd.DataFrame:
    df = calendario.rename(columns={"data": "data"})[
        ["data", "ano", "trimestre", "mes", "nome_mes", "dia_util"]
    ]
    return _upsert_dim(engine, df, "dim_tempo", ["data"])


def carregar_dim_produto(engine, vendas: pd.DataFrame) -> pd.DataFrame:
    df = vendas[["produto", "categoria_produto"]].drop_duplicates()
    df = df.rename(columns={"produto": "nome", "categoria_produto": "categoria"})
    return _upsert_dim(engine, df, "dim_produto", ["nome"])


def carregar_dim_cliente(engine, vendas: pd.DataFrame) -> pd.DataFrame:
    df = vendas[["cliente", "segmento", "regiao"]].drop_duplicates()
    df = df.rename(columns={"cliente": "nome"})
    return _upsert_dim(engine, df, "dim_cliente", ["nome"])


def carregar_dim_categoria_despesa(engine, despesas: pd.DataFrame) -> pd.DataFrame:
    df = despesas[["categoria_despesa"]].drop_duplicates().rename(columns={"categoria_despesa": "nome"})
    return _upsert_dim(engine, df, "dim_categoria_despesa", ["nome"])


def _tempo_por_data(dim_tempo: pd.DataFrame) -> pd.DataFrame:
    """Coage data para datetime (o banco devolve texto/date; o merge exige tipos iguais)."""
    df = dim_tempo[["data", "data_id"]].copy()
    df["data"] = pd.to_datetime(df["data"])
    return df


def carregar_fato_vendas(engine, vendas: pd.DataFrame, dim_tempo, dim_produto, dim_cliente):
    vendas = vendas.copy()
    vendas["data"] = pd.to_datetime(vendas["data"])
    df = vendas.merge(_tempo_por_data(dim_tempo), on="data")
    df = df.merge(dim_produto[["nome", "produto_id"]], left_on="produto", right_on="nome")
    df = df.merge(dim_cliente[["nome", "cliente_id"]], left_on="cliente", right_on="nome", suffixes=("", "_cli"))
    df = df[["data_id", "produto_id", "cliente_id", "receita", "quantidade"]]
    df.to_sql("fato_vendas", engine, if_exists="append", index=False)


def carregar_fato_despesas(engine, despesas: pd.DataFrame, dim_tempo, dim_categoria):
    despesas = despesas.copy()
    despesas["data"] = pd.to_datetime(despesas["data"])
    df = despesas.merge(_tempo_por_data(dim_tempo), on="data")
    df = df.merge(dim_categoria[["nome", "categoria_id"]], left_on="categoria_despesa", right_on="nome")
    df = df[["data_id", "categoria_id", "valor"]]
    df.to_sql("fato_despesas", engine, if_exists="append", index=False)


def main():
    engine = create_engine(DB_URL)
    calendario = pd.read_csv(f"{CLEAN_DIR}/calendario.csv", parse_dates=["data"])
    vendas = pd.read_csv(f"{CLEAN_DIR}/vendas.csv", parse_dates=["data"])
    despesas = pd.read_csv(f"{CLEAN_DIR}/despesas.csv", parse_dates=["data"])

    dim_tempo = carregar_dim_tempo(engine, calendario)
    dim_produto = carregar_dim_produto(engine, vendas)
    dim_cliente = carregar_dim_cliente(engine, vendas)
    dim_categoria = carregar_dim_categoria_despesa(engine, despesas)

    _limpar_fatos(engine)
    carregar_fato_vendas(engine, vendas, dim_tempo, dim_produto, dim_cliente)
    carregar_fato_despesas(engine, despesas, dim_tempo, dim_categoria)

    print("Carga concluída no Postgres.")


if __name__ == "__main__":
    main()
