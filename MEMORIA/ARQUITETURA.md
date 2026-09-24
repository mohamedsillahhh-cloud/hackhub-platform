# Arquitetura

## Visao geral

O repositorio e um monorepo com frontend Next.js e API FastAPI. Nginx faz o
proxy no ambiente Docker. SQLite e a persistencia suportada para uma instancia;
Redis e opcional e usado como cache de ranking e contador de utilizacao de IA.

## Backend

O codigo vive em `backend/app/`:

- `main.py`: composicao da aplicacao, middleware, routers, lifespan e handlers.
- `api/v1/endpoints/`: fronteira HTTP e dependencias de autenticacao.
- `schemas/`: contratos Pydantic de entrada e saida.
- `services/`: regras de negocio e autorizacao dependente do dominio.
- `repositories/`: consultas SQLAlchemy reutilizadas pelos servicos.
- `models/`: modelos ORM, constraints e relacoes.
- `core/`: configuracao, base de dados, JWT, sessoes e rate limiting.
- `utils/`: integracoes auxiliares de email e geracao de codigos.

`get_db` abre uma sessao por request, faz commit depois de uma resposta bem
sucedida e rollback quando ha excecao. Servicos usam `flush` para obter estado
na mesma transacao e nao fazem commit proprio. SQLite ativa foreign keys e WAL.

Alembic e a autoridade do schema persistente. `migration_bootstrap.py` apenas
reconhece uma base SQLite anterior ao Alembic e marca a revisao compativel antes
do `upgrade head`; nao substitui uma revisao para mudancas futuras. Criacao
automatica de tabelas e permitida apenas em desenvolvimento/teste.

Autenticacao usa access e refresh JWT ligados a `auth_sessions`. O hash do
refresh atual fica na base, permitindo rotacao, deteccao de reutilizacao e
revogacao. Tokens de acao de email permanecem fora desse fluxo.

## Frontend

O codigo vive em `frontend/src/`:

- `app/`: rotas do App Router; paginas interativas sao client components.
- `components/ui/`: primitives visuais baseadas em Radix/Tailwind.
- `components/forms/` e `components/shared/`: UI de dominio.
- `hooks/`: queries e mutations de TanStack Query.
- `lib/api.ts`: cliente Axios e renovacao coordenada de sessao.
- `store/`: estado local de autenticacao e tema em Zustand.
- `types/`: contratos TypeScript correspondentes a API.

O browser envia cookies com `withCredentials`. Um `401` tenta uma unica
renovacao; requests concorrentes aguardam a mesma renovacao. Convites de equipa
podem ser aceites ou recusados diretamente na notificacao.

## Execucao e validacao

- Desenvolvimento manual: FastAPI em `:8000` e Next.js em `:3000`.
- Docker Compose: frontend, backend, Redis e Nginx; SQLite usa volume proprio.
- O container backend executa bootstrap legado e `alembic upgrade head` antes
  de iniciar a API.
- `/health/live` verifica o processo; `/health/ready` consulta a base.
- Backend: pytest, flake8, black, isort e verificacao Alembic.
- Frontend: ESLint, TypeScript e build Next.js.
- CI executa verificacoes, migracao nova e build das imagens Docker.
