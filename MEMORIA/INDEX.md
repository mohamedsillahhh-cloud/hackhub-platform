# Índice da memória

Ler este índice antes de qualquer tarefa e abrir apenas os ficheiros indicados
para o tema em causa. O código continua a ser a fonte de verdade.

## Rotas

- Estado funcional, alcance e limitações: `MEMORIA/ESTADO.md`
- Estrutura de módulos, fronteiras e execução: `MEMORIA/ARQUITETURA.md`
- Entidades, relações e invariantes de dados: `MEMORIA/db/schema.md`
- Login, cookies, refresh, verificação e reset:
  `MEMORIA/fluxos/autenticacao.md`
- Evento, equipa, projeto, avaliação e ranking:
  `MEMORIA/fluxos/ciclo-evento.md`
- Dashboard público, administrativo e escopo de organizador:
  `MEMORIA/fluxos/dashboard.md`
- Razão para SQLite e Redis opcional:
  `MEMORIA/decisoes/001-sqlite-e-redis-opcional.md`
- Separação obrigatória entre tokens de email e sessão:
  `MEMORIA/problemas/tokens-de-acao-como-sessao.md`
- Propriedade única da política CORS:
  `MEMORIA/problemas/cors-no-proxy.md`

## Rotas reservadas

Criar apenas quando existir conhecimento durável correspondente:

- Discord: `MEMORIA/discord/`
- Informação histórica sem uso normal: `MEMORIA/arquivo/`

## Regras rápidas

- Cada facto vive num único ficheiro; usar referências em vez de duplicação.
- Não guardar histórico de sessões; usar `git log`.
- Não ler `MEMORIA/arquivo/` sem necessidade explícita.
- Manter cada ficheiro com no máximo 600 linhas.
