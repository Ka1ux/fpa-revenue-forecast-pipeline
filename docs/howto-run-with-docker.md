# Como rodar o pipeline completo com Postgres (Docker)

Este guia mostra como carregar os dados num Postgres real, usando a etapa `load` — a única que precisa de banco de dados. O resultado é o esquema estrela populado, pronto para o Power BI conectar via ODBC.

## Pré-requisitos

- Docker Desktop instalado e **em execução**
- As dependências Python já instaladas (`pip install -r requirements.txt`)

## Passos

1. Suba o Postgres:

   ```bash
   docker compose up -d
   ```

   O `docker-compose.yml` cria o banco `fpa` e roda `sql/schema.sql` automaticamente na primeira inicialização, criando as tabelas fato e dimensão.

2. Gere e limpe os dados (se ainda não fez):

   ```bash
   python -m etl.extract
   python -m etl.transform
   ```

3. Carregue no Postgres:

   ```bash
   python -m etl.load
   ```

   Você verá:

   ```
   Carga concluída no Postgres.
   ```

4. Gere o forecast:

   ```bash
   python -m forecast.scenarios
   ```

## Verificação

Confirme que as tabelas foram populadas:

```bash
docker compose exec postgres psql -U fpa -d fpa -c "SELECT COUNT(*) FROM fato_vendas;"
```

Deve retornar algo como `2655`. Rode `python -m etl.load` de novo e o número **não muda** — a carga é idempotente (as tabelas fato são esvaziadas antes de recarregar).

## Conectar o Power BI ao Postgres

No Power BI Desktop: **Obter dados > Banco de Dados PostgreSQL**, com:

- Servidor: `localhost:5432`
- Banco de dados: `fpa`
- Usuário: `fpa` / Senha: `fpa`

## Troubleshooting

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `bunx: command not found` no setup | — | Não se aplica ao `load`; ignore. |
| `could not connect to server` | Postgres não subiu | Confira `docker compose ps`; rode `docker compose up -d`. |
| `relation "fato_vendas" does not exist` | schema não rodou | Recrie o volume: `docker compose down -v && docker compose up -d`. |
| Números dobrados no Power BI | versão antiga do `load.py` | Atualize; a carga atual é idempotente. |

## Configuração alternativa de banco

Por padrão o `load` usa `postgresql://fpa:fpa@localhost:5432/fpa`. Para apontar para outro banco, defina a variável de ambiente:

```bash
export FPA_DB_URL="postgresql://usuario:senha@host:5432/banco"
python -m etl.load
```

## Relacionado

- [Tutorial de introdução](tutorial-getting-started.md)
- [Referência do pipeline](reference-pipeline.md)
