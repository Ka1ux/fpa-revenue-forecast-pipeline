# Tutorial: do zero ao forecast em 5 minutos

Ao final deste tutorial você terá rodado o pipeline inteiro sem Docker: dados gerados, limpos, e um forecast de receita e margem para os próximos 6 meses, com o impacto financeiro de cada cenário impresso na tela.

## O que você vai precisar

- Python 3.11 ou superior (`python --version` para conferir)
- `pip` para instalar as dependências
- Nenhum banco de dados nem Docker para este tutorial

## Passo 1: Instalar as dependências

Na raiz do projeto:

```bash
pip install -r requirements.txt
```

Isso instala pandas, numpy, statsmodels e o resto. Leva menos de um minuto.

## Passo 2: Gerar os dados

```bash
python -m etl.extract
```

Você verá:

```
Dados gerados em data/raw/
```

Isso criou `data/raw/vendas.csv`, `despesas.csv` e `calendario.csv` — três anos de dados simulados (2022-2024), com sazonalidade e um gap proposital em julho/2023.

## Passo 3: Limpar e checar qualidade

```bash
python -m etl.transform
```

Repare no relatório de qualidade que aparece:

```
[data_quality] vendas: 2655 linhas
  - nenhum problema encontrado
```

Os dados limpos vão para `data/clean/`.

## Passo 4: Rodar o forecast

```bash
python -m forecast.scenarios
```

Aqui está o primeiro resultado de negócio:

```
Impacto financeiro (margem acumulada, próx. 6 meses):
  Base:       R$ 442.500,60
  Otimista:   R$ 590.292,69  (+33.4% vs. base)
  Pessimista: R$ 217.361,08  (-50.9% vs. base)
```

Isso é o coração do projeto: três cenários de margem, com o impacto de cada um em relação ao caso base. O forecast detalhado (mês a mês) ficou em `data/forecast/cenarios.csv`.

## Passo 5: Preparar os dados do dashboard

```bash
python -m dashboard.export_powerbi
```

Isso monta `dashboard/fpa_dashboard.csv`, uma tabela única com realizado + os 3 cenários, pronta para o Power BI importar.

## O que você construiu

Em cinco comandos você rodou um pipeline de FP&A completo: ETL, forecast e a tabela do dashboard. A partir daqui:

- Para ver os gráficos da análise, abra `notebooks/analysis.ipynb` no VS Code e rode todas as células.
- Para montar o dashboard, siga [dashboard/GUIA_POWERBI.md](../dashboard/GUIA_POWERBI.md).
- Para carregar os dados num Postgres de verdade, veja o [how-to com Docker](howto-run-with-docker.md).
- Para entender por que o projeto foi feito assim, veja a [explicação de arquitetura](explanation-architecture.md).
