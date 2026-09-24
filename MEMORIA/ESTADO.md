# Estado do produto

## Visao atual

HackHub e uma aplicacao web para gerir hackathons. O repositorio tem uma base
pronta para implantacao controlada numa unica instancia com SQLite. Uma entrada
em producao continua dependente de configuracao de segredos, TLS, SMTP/Telegram,
backups, observabilidade externa e validacao de carga no ambiente de destino.

## Implementado

- Registo, login, refresh rotativo e logout com sessoes revogaveis e cookies
  HTTP-only.
- Verificacao de email e reset de palavra-passe com tokens de acao separados;
  reset e de uso unico e revoga todas as sessoes existentes.
- Perfil privado, estatisticas reais e papeis `admin`, `organizer`, `judge` e
  `participant`.
- CRUD e ciclo de estado de eventos: `draft -> published -> in_progress -> closed`;
  eventos publicados tambem podem voltar a `draft`.
- Equipas por evento, convites acionaveis, codigo de entrada, transferencia de
  lideranca, saida e remocao de membros.
- Um projeto por equipa, edicao pelo lider e submissao.
- Desafios, categorias e criterios ponderados por evento, com gestao no
  dashboard e apresentacao publica real.
- Avaliacoes de projetos submetidos por jurados/admins e ranking medio.
- Ranking por HTTP e stream SSE; Redis e cache opcional.
- Notificacoes persistidas; email e Telegram por `telegram_chat_id` sao
  integracoes opcionais.
- Certificados PDF com QR code, verificacao publica e deteccao de alteracao do
  snapshot assinado.
- Dashboard global de admin, dashboard limitado aos eventos do organizador,
  metricas publicas reduzidas, estatisticas de evento e exportacao CSV/XLSX.
- Assistente de evento, feedback de projeto e sugestao heuristica de equipas;
  chamadas ao fornecedor dependem de `OPENAI_API_KEY`.
- Migracoes Alembic para instalacao nova e atualizacao da base SQLite legada.
- Health checks, request IDs, logs estruturados, trusted hosts, headers de
  seguranca e rate limiting.
- Interface Next.js para todos os fluxos acima, incluindo verificacao publica
  de certificados.

## Parcial ou limitado

- SQLite e o caminho suportado para uma unica instancia. Escala horizontal ou
  concorrencia elevada requerem uma base servidor e validacao propria.
- Redis nao e obrigatorio. Sem Redis, ranking funciona sem cache e limites
  diarios de tokens de IA ficam desativados.
- Sugestao de equipas usa perfis globais e uma heuristica por competencias;
  nao existe entidade de inscricao independente da equipa.
- Notificacoes push sao apenas registos internos; nao existe service worker.
- Certificados usam hash autenticado no servidor, nao assinatura PDF publica
  baseada em certificado digital.
- Nao existe WebSocket; o tempo real de ranking usa SSE.
- Entrega SMTP, Telegram e chamadas OpenAI nao sao cobertas pela suite local
  sem credenciais reais; devem ser exercitadas em staging.

## Fora do estado atual

- Celery e processamento distribuido de tarefas.
- Dominios personalizados e faturacao dos planos de organizacao.
- Upload e armazenamento proprio de ficheiros/media.
- Atribuicao explicita de jurados a eventos ou projetos.
