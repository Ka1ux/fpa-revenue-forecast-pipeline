# Todas as medidas DAX do projeto

Lista completa e organizada. **Todas** podem ser criadas na sua tabela `Medidas`
(elas referenciam a coluna de origem explicitamente, então a tabela onde ficam
guardadas não importa). São 19 medidas.

Como criar cada uma: clique na tabela `Medidas` > **Nova medida** > cole o código > Enter.

Pré-requisito de dados importados:
- `fpa_dashboard` (de `dashboard/fpa_dashboard.csv`) — usada nos KPIs, tendência e cenários
- `vendas` (de `data/clean/vendas.csv`) — usada na página de receita em detalhe
- `despesas` (de `data/clean/despesas.csv`) — usada na página de despesas

---

## 1. KPIs base (tabela fpa_dashboard)

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

## 2. Variação no tempo

```dax
Receita Mes Anterior =
CALCULATE([Receita Total], DATEADD(fpa_dashboard[data], -1, MONTH))
```
```dax
Variacao Receita MoM % =
DIVIDE([Receita Total] - [Receita Mes Anterior], [Receita Mes Anterior])
```

## 3. Alerta de desvio

```dax
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

## 4. KPI Positivo / Negativo (cartão colorido)

```dax
Status Margem = IF([Margem Total] >= 0, "▲ Positivo", "▼ Negativo")
```
```dax
Cor Status = IF([Margem Total] >= 0, "#2ECC71", "#E74C3C")
```
```dax
Status Tendencia = IF([Variacao Receita MoM %] >= 0, "▲ Crescendo", "▼ Caindo")
```

## 5. Comparação de cenários (tabela fpa_dashboard)

```dax
Margem Base =
CALCULATE(
    [Margem Total],
    FILTER(ALL(fpa_dashboard[cenario]), fpa_dashboard[cenario] = "base")
)
```
```dax
Margem vs Base = [Margem Total] - [Margem Base]
```
```dax
Margem vs Base % = DIVIDE([Margem vs Base], [Margem Base])
```

## 6. Receita em detalhe (tabela vendas)

```dax
Receita Vendas = SUM(vendas[receita])
```
```dax
Qtd Vendida = SUM(vendas[quantidade])
```
```dax
Ticket Medio = DIVIDE([Receita Vendas], [Qtd Vendida])
```
```dax
% Receita = DIVIDE([Receita Vendas], CALCULATE([Receita Vendas], ALLSELECTED(vendas)))
```

## 7. Despesas (tabela despesas)

```dax
Despesa Detalhe = SUM(despesas[valor])
```
```dax
% Despesa = DIVIDE([Despesa Detalhe], CALCULATE([Despesa Detalhe], ALLSELECTED(despesas)))
```

---

## Quais medidas cada KPI da imagem usa

| KPI na imagem | Medida |
|---|---|
| Receita Total | `Receita Total` |
| Despesa Total | `Despesa Total` |
| Margem Total | `Margem Total` |
| Margem % | `Margem %` |
| Ticket Médio | `Ticket Medio` |
| Status Margem (Positivo/Negativo) | `Status Margem` + `Cor Status` |
| Produto/Região líder | use o visual (arraste `produto`/`regiao` + `Receita Vendas`, ordene desc) |
| % Folha, Maior categoria | `% Despesa` + visual de `categoria_despesa` |
| Margem base/otimista/pessimista | `Margem Total` filtrada por `cenario` |
| Spread (otim - pess) | crie: `Spread Margem = [Margem otimista] - [Margem pessimista]` (opcional) |

> Nota sobre time intelligence: `Receita Mes Anterior` usa `DATEADD`, que funciona
> melhor com uma **tabela de datas** marcada. Se o Power BI reclamar, crie uma tabela
> de calendário (`Nova tabela > Calendario = CALENDARAUTO()`) e marque-a como tabela de
> datas. Com dados mensais simples, `DATEADD(...,-1,MONTH)` costuma funcionar direto.
