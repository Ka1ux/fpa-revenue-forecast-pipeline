# Referência do pipeline

Descrição técnica completa dos módulos, do esquema de dados e dos artefatos gerados.

## Módulos e comandos

Todos os módulos rodam como `python -m <modulo>` a partir da raiz do projeto.

### `etl.extract`

Gera os dados simulados. Sem argumentos.

| Constante | Valor | Efeito |
|-----------|-------|--------|
| `START_DATE` / `END_DATE` | `2022-01-01` / `2024-12-31` | Janela dos dados |
| seed | `42` | Torna a geração reprodutível |

Saídas: `data/raw/calendario.csv`, `vendas.csv`, `despesas.csv`. As vendas têm sazonalidade (pico no Q4), tendência de crescimento (~15%/ano) e um gap proposital de uma semana em julho/2023.

### `etl.transform`

Lê `data/raw/`, aplica limpeza e checagens de qualidade, grava em `data/clean/`.

Checagens em vendas: remoção de duplicatas, receita negativa e linhas nulas. Em despesas: valor negativo. Cada execução imprime um relatório `[data_quality]` por dataset.

### `etl.load`

Carrega `data/clean/` no Postgres seguindo o esquema estrela. Idempotente: as tabelas fato são esvaziadas (`DELETE`) antes de recarregar; as dimensões usam upsert por chave normalizada.

| Variável de ambiente | Padrão |
|----------------------|--------|
| `FPA_DB_URL` | `postgresql://fpa:fpa@localhost:5432/fpa` |

### `forecast.scenarios`

Lê `data/clean/`, projeta 6 meses e grava `data/forecast/cenarios.csv`.

Cenários (deltas aplicados sobre a projeção base):

| Cenário | `receita_delta` | `custo_delta` |
|---------|-----------------|---------------|
| base | 0% | 0% |
| otimista | +10% | -5% |
| pessimista | -15% | +8% |

Parâmetro `n_meses` (padrão 6) controla o horizonte.

### `dashboard.export_powerbi`

Combina realizado + cenários numa tabela única `dashboard/fpa_dashboard.csv` (formato tidy, UTF-8 com BOM para o Power BI).

### `dashboard.render_mockup` / `dashboard.render_pages`

Geram as imagens PNG de referência do dashboard a partir dos dados reais.

## Esquema de dados (`sql/schema.sql`)

### Dimensões

| Tabela | Chave | Colunas |
|--------|-------|---------|
| `dim_tempo` | `data_id` | data, ano, trimestre, mes, nome_mes, dia_util |
| `dim_produto` | `produto_id` | nome, categoria |
| `dim_cliente` | `cliente_id` | nome, segmento, regiao |
| `dim_categoria_despesa` | `categoria_id` | nome |

### Fatos

| Tabela | Chave | Colunas | FKs |
|--------|-------|---------|-----|
| `fato_vendas` | `venda_id` | receita, quantidade | data_id, produto_id, cliente_id |
| `fato_despesas` | `despesa_id` | valor | data_id, categoria_id |

## Artefatos gerados

| Arquivo | Gerado por | Conteúdo |
|---------|-----------|----------|
| `data/raw/*.csv` | `etl.extract` | Dados brutos simulados |
| `data/clean/*.csv` | `etl.transform` | Dados limpos |
| `data/forecast/cenarios.csv` | `forecast.scenarios` | Forecast mês × cenário |
| `dashboard/fpa_dashboard.csv` | `dashboard.export_powerbi` | Tabela do dashboard |

> Os CSVs estão no `.gitignore` (dados gerados, reprodutíveis via seed fixo). Não são versionados.

## `dashboard/fpa_dashboard.csv` — colunas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `data` | data | Primeiro dia do mês |
| `tipo` | texto | `Realizado` ou `Previsto` |
| `cenario` | texto | `Realizado`, `base`, `otimista`, `pessimista` |
| `receita_valor` / `despesa_valor` / `margem_valor` | número | Valores mensais |
| `ano` / `mes` / `ano_mes` | — | Colunas de calendário |

## Relacionado

- [Tutorial de introdução](tutorial-getting-started.md)
- [Como rodar com Docker](howto-run-with-docker.md)
- [Explicação de arquitetura](explanation-architecture.md)
- [Medidas DAX do dashboard](../dashboard/TODAS_AS_MEDIDAS_DAX.md)
