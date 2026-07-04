# Guia — Montar o dashboard no Power BI Desktop

Tempo estimado: ~15-20 min. Você importa **1 arquivo**, cola as medidas DAX e monta 4 visuais.

O arquivo de dados já está pronto: `dashboard/fpa_dashboard.csv`. Se ele não existir, gere com:
```powershell
python -m dashboard.export_powerbi
```

---

## Passo 1 — Importar os dados

1. Abra o Power BI Desktop.
2. **Página Inicial > Obter dados > Texto/CSV**.
3. Selecione `dashboard/fpa_dashboard.csv`.
4. Na prévia, confira que os números vieram como número (não texto). Clique **Carregar**.

A tabela se chama `fpa_dashboard`. Colunas:
- `data`, `ano`, `mes`, `ano_mes` — calendário
- `tipo` — "Realizado" ou "Previsto"
- `cenario` — "Realizado", "base", "otimista", "pessimista"
- `receita_valor`, `despesa_valor`, `margem_valor`

---

## Passo 2 — Criar as medidas DAX

Clique com o botão direito na tabela `fpa_dashboard` no painel **Dados** > **Nova medida**. Cole cada uma abaixo (uma de cada vez):

```dax
Receita Total = SUM(fpa_dashboard[receita_valor])
```

```dax
Despesa Total = SUM(fpa_dashboard[despesa_valor])
```

```dax
Margem Total = SUM(fpa_dashboard[margem_valor])
```

```dax
Margem % = DIVIDE([Margem Total], [Receita Total])
```

```dax
Receita Mes Anterior =
CALCULATE(
    [Receita Total],
    DATEADD(fpa_dashboard[data], -1, MONTH)
)
```

```dax
Variacao Receita MoM % =
DIVIDE(
    [Receita Total] - [Receita Mes Anterior],
    [Receita Mes Anterior]
)
```

```dax
-- Alerta de desvio: sinaliza quando a margem prevista de um cenario
-- cai mais de 20% frente ao cenario base no mesmo mes.
Alerta Desvio Margem =
VAR MargemBase =
    CALCULATE(
        [Margem Total],
        FILTER(ALL(fpa_dashboard[cenario]), fpa_dashboard[cenario] = "base")
    )
VAR MargemAtual = [Margem Total]
RETURN
    IF(
        AND(MargemBase <> 0, DIVIDE(MargemAtual - MargemBase, MargemBase) < -0.2),
        "⚠ Desvio",
        "OK"
    )
```

---

## Passo 3 — Montar os visuais

### A) Cartões de KPI (topo)
Insira 4 visuais do tipo **Cartão** (Card), um para cada medida:
- Receita Total
- Despesa Total
- Margem Total
- Margem %

### B) Tendência de receita (linha)
1. Visual **Gráfico de linhas**.
2. **Eixo X:** `data` (ou `ano_mes`).
3. **Eixo Y:** `Receita Total`.
4. **Legenda:** `cenario` — assim aparecem as 4 linhas (Realizado + base/otimista/pessimista) na mesma tela.

### C) Margem por cenário (colunas)
1. Visual **Gráfico de colunas agrupadas**.
2. **Eixo X:** `cenario`.
3. **Eixo Y:** `Margem Total`.
4. Filtre para `tipo = "Previsto"` (no painel de Filtros) para comparar só os cenários futuros.

### D) Variação mensal + alerta (tabela)
1. Visual **Tabela**.
2. Colunas: `ano_mes`, `Receita Total`, `Variacao Receita MoM %`, `Alerta Desvio Margem`.
3. Em **Formatação condicional** na coluna do alerta, deixe "⚠ Desvio" em vermelho.

### Segmentações (filtros)
Adicione 2 **Segmentações de dados** (Slicer): uma por `ano`, outra por `cenario`. Deixa o dashboard interativo.

---

## Passo 4 — Salvar

**Arquivo > Salvar como** > `dashboard/revenue_dashboard.pbix`.

Pronto. Esse é o `.pbix` do projeto — agora gerado pelo próprio Power BI (a única forma de gerar um `.pbix` válido).

---

## Páginas extras (dashboard multi-página)

Imagens de referência geradas dos dados reais (rode `python -m dashboard.render_pages`):
- `dashboard/page2_receita_detalhe.png`
- `dashboard/page3_despesas.png`
- `dashboard/page4_forecast.png`

Para as páginas 2 e 3, importe também as tabelas detalhadas (têm as colunas de
dimensão para fatiar): **Obter dados > Texto/CSV** em `data/clean/vendas.csv` e
`data/clean/despesas.csv`.

### Página 2 — Receita em Detalhe (tabela `vendas`)
- **Gráfico de barras** — Eixo Y: `produto` · Eixo X: soma de `receita`.
- **Gráfico de barras** — Eixo Y: `segmento` · Eixo X: soma de `receita`.
- **Gráfico de barras** — Eixo Y: `regiao` · Eixo X: soma de `receita`.
- **Matriz** — Linhas: `produto` · Colunas: `segmento` · Valores: soma de `receita`.

### Página 3 — Despesas por Categoria (tabela `despesas`)
- **Gráfico de área empilhada** — Eixo X: `data` · Eixo Y: soma de `valor` · Legenda: `categoria_despesa`.
- **Gráfico de barras** — Eixo Y: `categoria_despesa` · Eixo X: soma de `valor`.
- **Gráfico de pizza** — Legenda: `categoria_despesa` · Valores: soma de `valor`.

### Página 4 — Comparação de Cenários (tabela `fpa_dashboard`, filtro `tipo = "Previsto"`)
- **Colunas agrupadas** — Eixo X: métrica · Legenda: `cenario` (compare receita/despesa/margem).
- **Gráfico de linhas** — Eixo X: `data` · Eixo Y: `Margem Total` · Legenda: `cenario`.
- **Matriz** — Linhas: `ano_mes` · Colunas: `cenario` · Valores: `Margem Total`.

## Dica pra entrevista

O alerta de desvio (`Alerta Desvio Margem`) é o detalhe que mostra "pensamento de negócio": não é só um gráfico bonito, é uma regra que dispara quando um cenário de risco corrói a margem além de um limite. Saber explicar essa medida vale mais que qualquer visual.
