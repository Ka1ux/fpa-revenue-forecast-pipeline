"""Renders reference images for the extra dashboard pages.

Reads the real cleaned data (vendas, despesas) and the forecast to build three
layout-reference PNGs:
  - page 2: revenue detail (by product / segment / region)
  - page 3: expenses by category
  - page 4: forecast scenario comparison

These mirror what to build in Power BI. For pages 2-3 in Power BI, import the
detailed facts (data/clean/vendas.csv and data/clean/despesas.csv) directly —
they carry every dimension column needed to slice.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

CLEAN = "data/clean"
FORECAST = "data/forecast"

PALETA = ["#2e86de", "#27ae60", "#e67e22", "#8e44ad", "#e74c3c", "#16a085"]


def brl(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def _fmt_k(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))


def _barh(ax, serie, titulo):
    serie = serie.sort_values()
    cores = [PALETA[i % len(PALETA)] for i in range(len(serie))]
    ax.barh(serie.index, serie.values, color=cores)
    ax.set_title(titulo, fontsize=12, fontweight="bold", loc="left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    for i, v in enumerate(serie.values):
        ax.text(v, i, " " + brl(v), va="center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)


# ---------------------------------------------------------------- Página 2
def pagina_receita_detalhe(vendas):
    fig = plt.figure(figsize=(15, 8), facecolor="white")
    fig.suptitle("FP&A — Receita em Detalhe", fontsize=19, fontweight="bold", y=0.98)
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.35)

    _barh(fig.add_subplot(gs[0, 0]), vendas.groupby("produto")["receita"].sum(), "Receita por produto")
    _barh(fig.add_subplot(gs[0, 1]), vendas.groupby("segmento")["receita"].sum(), "Receita por segmento de cliente")
    _barh(fig.add_subplot(gs[1, 0]), vendas.groupby("regiao")["receita"].sum(), "Receita por região")

    # tabela top produtos x segmento
    ax = fig.add_subplot(gs[1, 1])
    ax.axis("off")
    ax.set_title("Receita: produto × segmento", fontsize=12, fontweight="bold", loc="left")
    piv = vendas.pivot_table(index="produto", columns="segmento", values="receita", aggfunc="sum", fill_value=0)
    texto = [[brl(piv.loc[p, c]) for c in piv.columns] for p in piv.index]
    tab = ax.table(cellText=texto, rowLabels=list(piv.index), colLabels=list(piv.columns), cellLoc="center", loc="center")
    tab.auto_set_font_size(False)
    tab.set_fontsize(7.5)
    tab.scale(1, 1.5)
    for (row, col), cell in tab.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1f2a44")
            cell.set_text_props(color="white", fontweight="bold")

    fig.savefig("dashboard/page2_receita_detalhe.png", dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Página 3
def pagina_despesas(despesas):
    despesas = despesas.copy()
    despesas["data"] = pd.to_datetime(despesas["data"])
    fig = plt.figure(figsize=(15, 8), facecolor="white")
    fig.suptitle("FP&A — Despesas por Categoria", fontsize=19, fontweight="bold", y=0.98)
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3, height_ratios=[1.3, 1])

    # área empilhada mensal
    ax1 = fig.add_subplot(gs[0, :])
    piv = despesas.pivot_table(index="data", columns="categoria_despesa", values="valor", aggfunc="sum", fill_value=0)
    ax1.stackplot(piv.index, [piv[c] for c in piv.columns], labels=list(piv.columns), colors=PALETA[: len(piv.columns)], alpha=0.85)
    ax1.set_title("Despesas mensais por categoria (empilhado)", fontsize=12, fontweight="bold", loc="left")
    _fmt_k(ax1)
    ax1.legend(loc="upper left", fontsize=8, ncol=len(piv.columns))
    ax1.spines[["top", "right"]].set_visible(False)

    # total por categoria
    _barh(fig.add_subplot(gs[1, 0]), despesas.groupby("categoria_despesa")["valor"].sum(), "Total por categoria")

    # participação (%)
    ax3 = fig.add_subplot(gs[1, 1])
    total_cat = despesas.groupby("categoria_despesa")["valor"].sum()
    ax3.pie(total_cat.values, labels=total_cat.index, autopct="%1.0f%%", colors=PALETA[: len(total_cat)], textprops={"fontsize": 8})
    ax3.set_title("Participação no total de despesas", fontsize=12, fontweight="bold", loc="left")

    fig.savefig("dashboard/page3_despesas.png", dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Página 4
def pagina_forecast(cenarios):
    cenarios = cenarios.copy()
    cenarios["data"] = pd.to_datetime(cenarios["data"])
    cores = {"base": "#2e86de", "otimista": "#27ae60", "pessimista": "#e74c3c"}
    ordem = ["pessimista", "base", "otimista"]

    fig = plt.figure(figsize=(15, 8), facecolor="white")
    fig.suptitle("FP&A — Comparação de Cenários (Forecast)", fontsize=19, fontweight="bold", y=0.98)
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

    # receita/despesa/margem acumuladas por cenario (barras agrupadas)
    ax1 = fig.add_subplot(gs[0, :])
    metricas = ["receita_prevista", "despesa_prevista", "margem_prevista"]
    rotulos = ["Receita", "Despesa", "Margem"]
    import numpy as np

    x = np.arange(len(rotulos))
    largura = 0.25
    for i, cen in enumerate(ordem):
        g = cenarios[cenarios["cenario"] == cen][metricas].sum()
        ax1.bar(x + (i - 1) * largura, g.values, largura, label=cen, color=cores[cen])
    ax1.set_xticks(x)
    ax1.set_xticklabels(rotulos)
    ax1.set_title("Receita, despesa e margem acumuladas (próx. 6 meses) por cenário", fontsize=12, fontweight="bold", loc="left")
    _fmt_k(ax1)
    ax1.legend(fontsize=9)
    ax1.spines[["top", "right"]].set_visible(False)

    # margem mês a mês por cenário (linhas)
    ax2 = fig.add_subplot(gs[1, 0])
    for cen in ordem:
        g = cenarios[cenarios["cenario"] == cen].sort_values("data")
        ax2.plot(g["data"], g["margem_prevista"], marker="o", ms=4, color=cores[cen], label=cen)
    ax2.set_title("Margem prevista mês a mês", fontsize=12, fontweight="bold", loc="left")
    _fmt_k(ax2)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    # tabela mês × cenário (margem)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis("off")
    ax3.set_title("Margem prevista: mês × cenário", fontsize=12, fontweight="bold", loc="left")
    piv = cenarios.pivot_table(index="data", columns="cenario", values="margem_prevista", aggfunc="sum")[ordem]
    piv.index = piv.index.strftime("%Y-%m")
    texto = [[brl(piv.loc[m, c]) for c in ordem] for m in piv.index]
    tab = ax3.table(cellText=texto, rowLabels=list(piv.index), colLabels=ordem, cellLoc="center", loc="center")
    tab.auto_set_font_size(False)
    tab.set_fontsize(8)
    tab.scale(1, 1.5)
    for (row, col), cell in tab.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1f2a44")
            cell.set_text_props(color="white", fontweight="bold")

    fig.savefig("dashboard/page4_forecast.png", dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    vendas = pd.read_csv(f"{CLEAN}/vendas.csv", parse_dates=["data"])
    despesas = pd.read_csv(f"{CLEAN}/despesas.csv", parse_dates=["data"])
    cenarios = pd.read_csv(f"{FORECAST}/cenarios.csv", parse_dates=["data"])

    pagina_receita_detalhe(vendas)
    pagina_despesas(despesas)
    pagina_forecast(cenarios)
    print("Imagens geradas: page2_receita_detalhe.png, page3_despesas.png, page4_forecast.png")


if __name__ == "__main__":
    main()
