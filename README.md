# FP&A Revenue & Budget Forecasting Pipeline

Pipeline completo de FP&A (Financial Planning & Analysis): do ETL de vendas, despesas e calendário até um dashboard executivo em Power BI, passando por modelagem dimensional em SQL e forecast de receita e margem em três cenários.

Projeto de portfólio — prioriza clareza de arquitetura, decisões documentadas e narrativa de negócio sobre robustez de produção.

## O que este projeto faz

- **Coleta** dados de vendas, despesas e calendário (simulados, realistas).
- **Limpa e transforma** com checagens de qualidade automáticas.
- **Carrega** num banco SQL modelado em esquema estrela (fato + dimensões).
- **Prevê** receita e margem para os próximos 6 meses em 3 cenários (base, otimista, pessimista).
- **Mostra** tudo num dashboard executivo de 4 páginas no Power BI, com KPIs, tendência, comparação de cenários e alerta de desvio.

## Requisitos

| Ferramenta | Versão | Para quê |
|-----------|--------|----------|
| Python | 3.11+ (testado em 3.13) | ETL, forecast, gráficos |
| Docker Desktop | qualquer recente | subir o Postgres local (etapa `load`) |
| Power BI Desktop | grátis, Windows | abrir/editar o dashboard `.pbix` |
| pip | — | instalar as libs Python |

Bibliotecas Python (em `requirements.txt`): pandas, numpy, statsmodels, sqlalchemy, psycopg2-binary, jupyter, matplotlib.

> O Docker só é necessário para a etapa `load` (Postgres). O ETL, o forecast e o notebook rodam sem Docker.

## Instalação

```bash
git clone <url-do-repo>
cd fpa-revenue-forecast-pipeline
pip install -r requirements.txt
```

## Como rodar

### Opção 1 — Sem Docker (ETL + forecast + notebook)

```bash
python -m etl.extract          # gera dados simulados em data/raw/
python -m etl.transform        # limpa + checa qualidade -> data/clean/
python -m forecast.scenarios   # forecast dos 3 cenários -> data/forecast/
python -m dashboard.export_powerbi   # tabela pronta pro Power BI -> dashboard/fpa_dashboard.csv
```

Para ver a análise com gráficos, abra `notebooks/analysis.ipynb` no VS Code ou Jupyter e rode todas as células.

### Opção 2 — Com Docker (pipeline completo, incluindo o Postgres)

```bash
docker compose up -d           # sobe o Postgres (schema criado automaticamente)
python -m etl.extract
python -m etl.transform
python -m etl.load             # carrega no Postgres (esquema estrela)
python -m forecast.scenarios
```

Conexão do banco (usada pelo `load` e pelo Power BI): `localhost:5432`, base `fpa`, usuário `fpa`, senha `fpa`. Sobrescreva com a variável `FPA_DB_URL` se precisar.

A carga é **idempotente** — rodar `load` mais de uma vez não duplica linhas.

## O dashboard (Power BI)

O arquivo pronto está em `dashboard/FP&A-PowerBI.pbix` (4 páginas). Se quiser montar do zero ou entender as medidas:

- **`dashboard/GUIA_POWERBI.md`** — passo a passo: importar dados, montar cada visual, aplicar formatação.
- **`dashboard/TODAS_AS_MEDIDAS_DAX.md`** — as 19 medidas DAX organizadas, prontas pra colar.

Páginas de referência:

**| Página |Conteúdo |**

| 1 — Visão Executiva  | KPIs, tendência, cenários, alerta |
| 2 — Receita em Detalhe | Por produto, segmento, região |
| 3 — Despesas | Evolução por categoria, participação |
| 4 — Cenários | Comparação base/otimista/pessimista |

## Documentação

Documentação completa em [`docs/`](docs/), organizada pelo framework Diataxis:

- [Tutorial](docs/tutorial-getting-started.md) — rodar o pipeline do zero
- [How-to: Docker/Postgres](docs/howto-run-with-docker.md) — carga completa no banco
- [Referência](docs/reference-pipeline.md) — módulos, esquema e artefatos
- [Explicação](docs/explanation-architecture.md) — decisões de arquitetura

## Estrutura do projeto

```
etl/
  extract.py        gera os dados simulados (vendas, despesas, calendário)
  transform.py      limpeza + checagens de qualidade
  load.py           carga idempotente no Postgres (esquema estrela)
forecast/
  scenarios.py      forecast de receita e margem em 3 cenários
sql/
  schema.sql        dim_tempo, dim_produto, dim_cliente, dim_categoria_despesa, fato_vendas, fato_despesas
notebooks/
  analysis.ipynb    EDA + validação do forecast + limitações
dashboard/
  FP&A-PowerBI.pbix         dashboard final (4 páginas)
  export_powerbi.py         gera a tabela única pro Power BI
  render_mockup.py          gera a imagem da página 1
  render_pages.py           gera as imagens das páginas 2-4
  GUIA_POWERBI.md           guia de montagem
  TODAS_AS_MEDIDAS_DAX.md   todas as medidas DAX
docker-compose.yml          Postgres local
requirements.txt
```

## Modelo de dados (esquema estrela)

- **Fatos:** `fato_vendas` (receita, quantidade), `fato_despesas` (valor)
- **Dimensões:** `dim_tempo` (data, mês, trimestre, dia útil), `dim_produto`, `dim_cliente` (segmento, região), `dim_categoria_despesa`

## Forecast

Método simples e explicável: **decomposição sazonal + tendência linear**, projetando 6 meses. Três cenários:

| Cenário | Receita | Custo |
|---------|---------|-------|
| Base | projeção direta | projeção direta |
| Otimista | +10% | -5% |
| Pessimista | -15% | +8% |

Cada cenário mostra o impacto na margem — no pessimista, a margem chega a ficar **negativa** em um mês, o que dispara o alerta de desvio no dashboard.

## Decisões de arquitetura

- **Dados simulados, não públicos reais.** Datasets públicos com granularidade mensal + calendário fiscal são raros e sujos; uma base simulada com sazonalidade, ruído e um gap proposital de ingestão serve melhor ao objetivo de portfólio.
- **Forecast simples e explicado, não ML complexo.** O valor está em explicar o método e suas limitações, não em maximizar acurácia.
- **Postgres via Docker, não SQLite.** Esquema estrela em Postgres é o vocabulário técnico esperado em entrevistas de dados/FP&A.
- **Power BI só como camada visual.** Toda a lógica de transformação e forecast vive em Python/SQL versionado.

## Licença

MIT — veja [LICENSE](LICENSE).

## Limitações conhecidas (fora de escopo por agora)

- Sem orquestração automática (Airflow/cron) — próximo passo natural.
- Forecast sem intervalo de confiança (estimativas pontuais).
- Sazonalidade assume repetição idêntica ano a ano; não captura choques de mercado.
- Volume de dados pequeno (meses, não anos em escala).
