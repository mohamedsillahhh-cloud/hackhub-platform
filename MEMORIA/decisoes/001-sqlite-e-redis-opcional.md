# Decisao 001: SQLite principal e Redis opcional

## Contexto

O projeto comecou documentado e configurado para PostgreSQL, mas o codigo foi
migrado para tipos portateis e SQLite para simplificar execucao local e a
distribuicao atual.

## Decisao

- SQLite com `aiosqlite` e a persistencia padrao e a usada pelo Docker atual.
- A base Docker vive em volume persistente separado.
- Alembic versiona o schema; criacao automatica de tabelas e apenas uma
  conveniencia de desenvolvimento/teste. SQLite usa WAL e foreign keys.
- Redis nao e requisito de disponibilidade: acelera ranking e guarda contagem
  diaria de tokens de IA, mas falhas degradam para execucao sem cache.
- PostgreSQL nao faz parte do caminho suportado atual, embora os modelos usem
  abstracoes SQLAlchemy portateis sempre que possivel.

## Consequencias

O setup fica pequeno e os testes usam SQLite em memoria. O container aplica
migracoes antes de iniciar. Antes de concorrencia alta ou producao
multi-instancia, sera necessario escolher uma base servidor e rever isolamento,
pooling e as constraints dependentes do dialeto.
