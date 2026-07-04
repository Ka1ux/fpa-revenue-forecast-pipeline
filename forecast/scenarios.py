"""Forecast de receita e margem: decomposição sazonal + tendência linear, 3 cenários."""
import os

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

CLEAN_DIR = "data/clean"
OUT_DIR = "data/forecast"

CENARIOS = {
    "base": {"receita_delta": 0.0, "custo_delta": 0.0},
    "otimista": {"receita_delta": 0.10, "custo_delta": -0.05},
    "pessimista": {"receita_delta": -0.15, "custo_delta": 0.08},
}


def receita_mensal() -> pd.Series:
    df = pd.read_csv(f"{CLEAN_DIR}/vendas.csv", parse_dates=["data"])
    mensal = df.set_index("data")["receita"].resample("MS").sum()
    return mensal


def despesa_mensal() -> pd.Series:
    df = pd.read_csv(f"{CLEAN_DIR}/despesas.csv", parse_dates=["data"])
    mensal = df.set_index("data")["valor"].resample("MS").sum()
    return mensal


def prever_proximos_meses(serie: pd.Series, n_meses: int = 6) -> pd.Series:
    decomposicao = seasonal_decompose(serie, model="additive", period=12, extrapolate_trend="freq")
    tendencia = decomposicao.trend.dropna()

    # extrapola a tendência com regressão linear
    x = np.arange(len(tendencia))
    coef = np.polyfit(x, tendencia.values, 1)
    x_futuro = np.arange(len(tendencia), len(tendencia) + n_meses)
    tendencia_futura = np.polyval(coef, x_futuro)

    # reaplica a média sazonal por mês
    sazonalidade_media = decomposicao.seasonal.groupby(decomposicao.seasonal.index.month).mean()
    datas_futuras = pd.date_range(serie.index[-1] + pd.DateOffset(months=1), periods=n_meses, freq="MS")
    sazonalidade_futura = [sazonalidade_media[d.month] for d in datas_futuras]

    previsao = tendencia_futura + sazonalidade_futura
    return pd.Series(previsao, index=datas_futuras)


def gerar_cenarios(n_meses: int = 6) -> pd.DataFrame:
    receita = receita_mensal()
    despesa = despesa_mensal()

    receita_prevista = prever_proximos_meses(receita, n_meses)
    despesa_prevista = prever_proximos_meses(despesa, n_meses)

    linhas = []
    for cenario, deltas in CENARIOS.items():
        receita_cenario = receita_prevista * (1 + deltas["receita_delta"])
        despesa_cenario = despesa_prevista * (1 + deltas["custo_delta"])
        margem = receita_cenario - despesa_cenario
        for data in receita_prevista.index:
            linhas.append(
                {
                    "data": data,
                    "cenario": cenario,
                    "receita_prevista": round(receita_cenario[data], 2),
                    "despesa_prevista": round(despesa_cenario[data], 2),
                    "margem_prevista": round(margem[data], 2),
                }
            )
    return pd.DataFrame(linhas)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = gerar_cenarios()
    df.to_csv(f"{OUT_DIR}/cenarios.csv", index=False)

    base = df[df["cenario"] == "base"]["margem_prevista"].sum()
    otimista = df[df["cenario"] == "otimista"]["margem_prevista"].sum()
    pessimista = df[df["cenario"] == "pessimista"]["margem_prevista"].sum()

    print("Forecast gerado em data/forecast/cenarios.csv")
    print(f"\nImpacto financeiro (margem acumulada, próx. 6 meses):")
    print(f"  Base:       R$ {base:,.2f}")
    print(f"  Otimista:   R$ {otimista:,.2f}  ({(otimista/base - 1) * 100:+.1f}% vs. base)")
    print(f"  Pessimista: R$ {pessimista:,.2f}  ({(pessimista/base - 1) * 100:+.1f}% vs. base)")


if __name__ == "__main__":
    main()
