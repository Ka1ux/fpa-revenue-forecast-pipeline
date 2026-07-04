# FP&A Revenue & Budget Forecasting Pipeline

Pipeline completo de FP&A (Financial Planning & Analysis): ETL de vendas/despesas/calendário, modelagem dimensional em SQL, forecast de receita e margem em 3 cenários, e dashboard executivo em Power BI.

Projeto de portfólio — prioriza clareza de arquitetura e decisões documentadas sobre robustez de produção.

## Arquitetura

```
data/raw/          dados simulados: vendas, despesas, calendário
etl/
  extract.py        gera/lê os dados brutos
  transform.py       limpeza + checagens de qualidade
  load.py             carrega no Postgres (fato + dimensões)
forecast/
  scenarios.py         forecast em 3 cenários (base/otimista/pessimista)
sql/
  schema.sql            schema estrela: fato_vendas, fato_despesas, dim_tempo, dim_produto, dim_cliente
notebooks/
  analysis.ipynb          EDA + validação do forecast
dashboard/
  revenue_dashboard.pbix    dashboard executivo
docker-compose.yml           Postgres local
```

## Como rodar

```bash
docker compose up -d
python -m etl.extract
python -m etl.transform
python -m etl.load
python -m forecast.scenarios
```

## Decisões de arquitetura

- **Dados simulados, não públicos reais.** Datasets públicos de vendas com granularidade mensal + calendário fiscal são raros e sujos; uma base simulada realista (sazonalidade, ruído, gaps propositais) serve melhor o objetivo de portfólio sem gastar dias em limpeza.
- **Forecast simples e explicado, não um modelo de ML complexo.** Decomposição sazonal + regressão linear com tendência. O valor de entrevista está em explicar o método e suas limitações, não em maximizar acurácia.
- **Postgres via Docker, não SQLite.** Schema estrela em Postgres é o vocabulário técnico que entrevistas de dado/FP&A esperam.
- **Power BI é só a camada visual.** Toda a lógica de transformação e forecast vive em Python/SQL versionado.

## Limitações conhecidas (fora de escopo por agora)

- Sem orquestração real (Airflow/cron) — próximo passo natural, não implementado.
- Sem checagem de qualidade via framework pesado (Great Expectations) — validações customizadas simples em `transform.py`.
- Volume de dados pequeno (meses, não anos de dados em escala).
