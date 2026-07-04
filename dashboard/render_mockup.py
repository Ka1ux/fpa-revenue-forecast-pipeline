"""Renders a reference image of the executive dashboard from the real data.

Not a Power BI file — a layout reference (PNG) built from dashboard/fpa_dashboard.csv
so you can replicate the same visuals and arrangement in Power BI.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

CSV = "dashboard/fpa_dashboard.csv"
OUT = "dashboard/dashboard_preview.png"

CORES = {
    "Realizado": "#1f2a44",
    "base": "#2e86de",
    "otimista": "#27ae60",
    "pessimista": "#e74c3c",
}


def brl(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def main():
    df = pd.read_csv(CSV, parse_dates=["data"])
    real = df[df["tipo"] == "Realizado"].sort_values("data")
    prev = df[df["tipo"] == "Previsto"].sort_values("data")

    # KPIs sobre o realizado
    receita_total = real["receita_valor"].sum()
    despesa_total = real["despesa_valor"].sum()
    margem_total = real["margem_valor"].sum()
    margem_pct = margem_total / receita_total

    fig = plt.figure(figsize=(15, 9), facecolor="white")
    fig.suptitle("FP&A — Dashboard Executivo de Receita e Margem", fontsize=20, fontweight="bold", x=0.5, y=0.98)
    gs = fig.add_gridspec(3, 4, height_ratios=[0.7, 1.4, 1.2], hspace=0.45, wspace=0.3)

    # --- Linha 1: cartoes de KPI ---
    kpis = [
        ("Receita Total", brl(receita_total), "#2e86de"),
        ("Despesa Total", brl(despesa_total), "#e67e22"),
        ("Margem Total", brl(margem_total), "#27ae60"),
        ("Margem %", f"{margem_pct:.1%}", "#8e44ad"),
    ]
    for i, (titulo, valor, cor) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i])
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor=cor, alpha=0.08, edgecolor=cor, lw=1.5))
        ax.text(0.5, 0.62, valor, ha="center", va="center", fontsize=17, fontweight="bold", color=cor, transform=ax.transAxes)
        ax.text(0.5, 0.25, titulo, ha="center", va="center", fontsize=11, color="#555", transform=ax.transAxes)

    # --- Linha 2: tendencia de receita com cenarios ---
    ax1 = fig.add_subplot(gs[1, :])
    ax1.plot(real["data"], real["receita_valor"], color=CORES["Realizado"], lw=2.2, marker="o", ms=3, label="Realizado")
    for cen in ["base", "otimista", "pessimista"]:
        g = prev[prev["cenario"] == cen]
        # conecta o ultimo ponto realizado ao inicio do forecast
        ponte = pd.concat([real.tail(1), g])
        ax1.plot(ponte["data"], ponte["receita_valor"], color=CORES[cen], lw=2, ls="--", marker="o", ms=3, label=f"Forecast — {cen}")
    ax1.set_title("Receita mensal: realizado vs. cenários de forecast", fontsize=13, fontweight="bold", loc="left")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    ax1.set_ylabel("Receita (R$)")
    ax1.legend(loc="upper left", fontsize=9, ncol=2)
    ax1.grid(True, alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    # --- Linha 3a: margem prevista por cenario (barras) ---
    ax2 = fig.add_subplot(gs[2, :2])
    margem_por_cen = prev.groupby("cenario")["margem_valor"].sum().reindex(["pessimista", "base", "otimista"])
    barras = ax2.bar(margem_por_cen.index, margem_por_cen.values, color=[CORES[c] for c in margem_por_cen.index])
    ax2.set_title("Margem prevista acumulada por cenário (próx. 6 meses)", fontsize=13, fontweight="bold", loc="left")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    for b, v in zip(barras, margem_por_cen.values):
        ax2.text(b.get_x() + b.get_width() / 2, v, brl(v), ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.grid(True, axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    # --- Linha 3b: tabela de variacao mensal + alerta ---
    ax3 = fig.add_subplot(gs[2, 2:])
    ax3.axis("off")
    ax3.set_title("Variação mensal (realizado) + alerta de desvio", fontsize=13, fontweight="bold", loc="left")
    real = real.copy()
    real["mom"] = real["receita_valor"].pct_change()
    ultimos = real.tail(6)
    base_margem = prev[prev["cenario"] == "base"]["margem_valor"].sum()
    linhas = []
    for _, r in ultimos.iterrows():
        mom = r["mom"]
        mom_str = "—" if pd.isna(mom) else f"{mom:+.1%}"
        alerta = "⚠ Desvio" if (not pd.isna(mom) and mom < -0.15) else "OK"
        linhas.append([r["ano_mes"], brl(r["receita_valor"]), mom_str, alerta])
    tabela = ax3.table(
        cellText=linhas,
        colLabels=["Mês", "Receita", "Var. MoM", "Alerta"],
        cellLoc="center",
        loc="center",
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(9)
    tabela.scale(1, 1.6)
    for (row, col), cell in tabela.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1f2a44")
            cell.set_text_props(color="white", fontweight="bold")
        elif col == 3 and linhas[row - 1][3].startswith("⚠"):
            cell.set_facecolor("#fdecea")
            cell.set_text_props(color="#e74c3c", fontweight="bold")

    fig.savefig(OUT, dpi=110, bbox_inches="tight", facecolor="white")
    print(f"Imagem do dashboard salva em {OUT}")


if __name__ == "__main__":
    main()
