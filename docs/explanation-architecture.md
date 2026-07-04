# Explicação: por que o projeto é assim

Este documento cobre as decisões de arquitetura e os trade-offs por trás delas. Se você quer saber *como usar*, veja o [tutorial](tutorial-getting-started.md); aqui é o *por quê*.

## O problema

Um projeto de portfólio de FP&A precisa demonstrar quatro coisas ao mesmo tempo: ETL, modelagem de dados, forecast e visualização de negócio. O risco é cair em dois extremos: ou virar um notebook único que não mostra engenharia de dados, ou virar uma infraestrutura pesada que nunca fica pronta e ninguém consegue rodar.

O objetivo aqui não é rodar em produção. É contar uma história técnica clara e reprodutível, forte para entrevista.

## Decisão 1: dados simulados, não públicos reais

**Problema:** datasets públicos de vendas com granularidade mensal, calendário fiscal e estrutura pronta para cenários são raros e sujos. Limpar um dataset público imperfeito consumiria dias.

**Abordagem:** gerar uma base simulada realista, com sazonalidade (pico no Q4), tendência de crescimento e um gap proposital de ingestão em julho/2023. Seed fixo (`42`) garante reprodutibilidade.

**Trade-off:** perde-se o apelo de "dados do mundo real". Ganha-se controle total sobre as características dos dados (dá para garantir que o forecast tenha o que decompor) e um gap proposital que vira ótimo talking point sobre tratar dados imperfeitos.

## Decisão 2: forecast simples e explicável

**Problema:** um modelo de ML sofisticado (Prophet, ARIMA) impressiona no papel, mas numa entrevista o que conta é explicar o método e suas limitações.

**Abordagem:** decomposição sazonal + tendência linear, projetando 6 meses. Três cenários aplicam deltas de receita e custo sobre a projeção base.

**Trade-off:** acurácia menor que um modelo dedicado, e sem intervalo de confiança. Em troca, todo o método cabe em uma conversa e as limitações são honestas e defensáveis.

**Alternativas consideradas:** Prophet e ARIMA foram descartados por adicionarem dependências e complexidade sem ganho de narrativa para o objetivo de portfólio.

## Decisão 3: Postgres via Docker, não SQLite

**Problema:** SQLite seria mais simples, mas é visto como "brinquedo" em processos de dados/FP&A.

**Abordagem:** Postgres num container Docker, com esquema estrela (fato + dimensões) criado automaticamente na subida.

**Trade-off:** mais fricção de setup (precisa de Docker). Em troca, o vocabulário técnico é o certo — esquema estrela, ETL modular, carga idempotente.

## Decisão 4: Power BI só como camada visual

**Problema:** se a lógica de negócio vive dentro do arquivo `.pbix`, ela não é versionável nem revisável.

**Abordagem:** toda transformação e forecast ficam em Python/SQL no git. O Power BI só lê a tabela final e desenha. As medidas DAX (KPIs, variação, alerta) ficam documentadas em Markdown.

**Trade-off:** o Power BI faz menos "trabalho pesado" do que poderia. Em troca, o cérebro do projeto é auditável e roda sem abrir o Power BI.

## A arquitetura, em uma imagem

```
extract → transform → load → Postgres (esquema estrela)
                 │                          │
                 └──→ forecast ──┐          │
                                 ▼          ▼
                         export_powerbi → Power BI (.pbix)
```

## Por que a carga é idempotente

A etapa `load` esvazia as tabelas fato antes de recarregar e faz upsert nas dimensões por uma chave normalizada (datas comparadas como `YYYY-MM-DD` dos dois lados). Sem isso, rodar o pipeline duas vezes duplicava as linhas de fato — e os totais no dashboard ficavam silenciosamente errados. É o tipo de bug que passa despercebido até alguém perguntar por que a receita dobrou.

## Relacionado

- [Referência do pipeline](reference-pipeline.md)
- [Tutorial de introdução](tutorial-getting-started.md)
