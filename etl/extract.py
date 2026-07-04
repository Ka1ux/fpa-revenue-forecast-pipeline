"""Generates simulated but realistic sales, expense, and calendar data.

Real public datasets at this granularity (monthly revenue + fiscal calendar +
scenario-ready structure) are rare and messy. A simulated base with seasonality,
noise, and deliberate gaps serves the portfolio goal better than days spent
cleaning an imperfect public dataset.
"""
import numpy as np
import pandas as pd

START_DATE = "2022-01-01"
END_DATE = "2024-12-31"

PRODUTOS = [
    ("Plano Starter", "Assinatura"),
    ("Plano Pro", "Assinatura"),
    ("Plano Enterprise", "Assinatura"),
    ("Consultoria", "Serviço"),
    ("Add-on Analytics", "Add-on"),
]

CLIENTES = [
    ("Acme Corp", "Enterprise", "Sudeste"),
    ("Bravo Ltda", "SMB", "Sul"),
    ("Cactus Tech", "SMB", "Nordeste"),
    ("Delta Sistemas", "Mid-Market", "Sudeste"),
    ("Echo Varejo", "SMB", "Centro-Oeste"),
    ("Foxtrot Indústria", "Enterprise", "Sul"),
]

CATEGORIAS_DESPESA = ["Folha", "Marketing", "Infraestrutura", "G&A", "Vendas"]


def gerar_calendario() -> pd.DataFrame:
    datas = pd.date_range(START_DATE, END_DATE, freq="D")
    df = pd.DataFrame({"data": datas})
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["trimestre"] = df["data"].dt.quarter
    df["nome_mes"] = df["data"].dt.strftime("%B")
    df["dia_util"] = df["data"].dt.dayofweek < 5
    return df


def gerar_vendas(rng: np.random.Generator) -> pd.DataFrame:
    datas = pd.date_range(START_DATE, END_DATE, freq="D")
    rows = []
    for data in datas:
        if data.dayofweek >= 5:
            continue  # sem vendas em fins de semana, por simplicidade
        # sazonalidade: pico no Q4, vale em Jan/Fev
        sazonalidade = 1 + 0.35 * np.sin((data.month - 3) / 12 * 2 * np.pi)
        tendencia = 1 + 0.15 * (data.year - 2022)  # crescimento anual ~15%
        n_vendas_dia = rng.poisson(3 * sazonalidade * tendencia)
        for _ in range(n_vendas_dia):
            produto = PRODUTOS[rng.integers(0, len(PRODUTOS))]
            cliente = CLIENTES[rng.integers(0, len(CLIENTES))]
            base_preco = {"Assinatura": 1200, "Serviço": 5000, "Add-on": 300}[produto[1]]
            receita = round(base_preco * rng.uniform(0.7, 1.4), 2)
            quantidade = rng.integers(1, 5)
            rows.append(
                {
                    "data": data,
                    "produto": produto[0],
                    "categoria_produto": produto[1],
                    "cliente": cliente[0],
                    "segmento": cliente[1],
                    "regiao": cliente[2],
                    "receita": receita,
                    "quantidade": int(quantidade),
                }
            )
    df = pd.DataFrame(rows)
    # gap proposital: remove uma semana de dados em julho/2023 (simula falha de ingestão real)
    mask_gap = (df["data"] >= "2023-07-10") & (df["data"] <= "2023-07-16")
    return df.loc[~mask_gap].reset_index(drop=True)


def gerar_despesas(rng: np.random.Generator) -> pd.DataFrame:
    meses = pd.date_range(START_DATE, END_DATE, freq="MS")
    rows = []
    base_por_categoria = {
        "Folha": 40000,
        "Marketing": 15000,
        "Infraestrutura": 8000,
        "G&A": 10000,
        "Vendas": 12000,
    }
    for data in meses:
        crescimento = 1 + 0.10 * (data.year - 2022)
        for categoria in CATEGORIAS_DESPESA:
            valor = round(base_por_categoria[categoria] * crescimento * rng.uniform(0.9, 1.15), 2)
            rows.append({"data": data, "categoria_despesa": categoria, "valor": valor})
    return pd.DataFrame(rows)


def main():
    rng = np.random.default_rng(42)
    out_dir = "data/raw"
    gerar_calendario().to_csv(f"{out_dir}/calendario.csv", index=False)
    gerar_vendas(rng).to_csv(f"{out_dir}/vendas.csv", index=False)
    gerar_despesas(rng).to_csv(f"{out_dir}/despesas.csv", index=False)
    print("Dados gerados em data/raw/")


if __name__ == "__main__":
    main()
