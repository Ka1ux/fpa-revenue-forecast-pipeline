"""Gera uma tabela única (realizado + cenários) pronta para o Power BI."""
import os

import pandas as pd

CLEAN_DIR = "data/clean"
FORECAST_DIR = "data/forecast"
OUT = "dashboard/fpa_dashboard.csv"


def main():
    vendas = pd.read_csv(f"{CLEAN_DIR}/vendas.csv", parse_dates=["data"])
    despesas = pd.read_csv(f"{CLEAN_DIR}/despesas.csv", parse_dates=["data"])
    cenarios = pd.read_csv(f"{FORECAST_DIR}/cenarios.csv", parse_dates=["data"])

    # Atuais mensais
    receita = vendas.set_index("data")["receita"].resample("MS").sum()
    despesa = despesas.set_index("data")["valor"].resample("MS").sum()
    atuais = pd.DataFrame({"receita": receita, "despesa": despesa}).reset_index()
    atuais["margem"] = atuais["receita"] - atuais["despesa"]
    atuais["tipo"] = "Realizado"
    atuais["cenario"] = "Realizado"
    atuais = atuais.rename(columns={"receita": "receita_valor", "despesa": "despesa_valor", "margem": "margem_valor"})

    # Forecast (3 cenarios)
    prev = cenarios.rename(
        columns={
            "receita_prevista": "receita_valor",
            "despesa_prevista": "despesa_valor",
            "margem_prevista": "margem_valor",
        }
    )
    prev["tipo"] = "Previsto"

    # Empilha tudo numa tabela unica (formato tidy)
    cols = ["data", "tipo", "cenario", "receita_valor", "despesa_valor", "margem_valor"]
    df = pd.concat([atuais[cols], prev[cols]], ignore_index=True)
    df = df.sort_values(["data", "cenario"]).reset_index(drop=True)

    # Colunas de calendario uteis pro Power BI
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["ano_mes"] = df["data"].dt.strftime("%Y-%m")

    os.makedirs("dashboard", exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"Tabela dashboard-ready salva em {OUT} ({len(df)} linhas)")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
