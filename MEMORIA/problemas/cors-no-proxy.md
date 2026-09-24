# CORS tem um único proprietário

## Falha evitada

Nginx refletia qualquer header `Origin` com credenciais, enquanto FastAPI tinha
uma allowlist. Headers CORS no proxy podiam contradizer ou neutralizar a política
da aplicação.

## Invariante

FastAPI é o único proprietário de CORS e usa `CORS_ORIGINS`. Nginx apenas faz
proxy de `/api/` e não adiciona headers nem respostas preflight próprios.
