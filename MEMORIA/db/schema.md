# Schema da base de dados

## Persistencia

SQLAlchemy assincrono sobre SQLite (`sqlite+aiosqlite`). IDs sao UUIDs gerados
na aplicacao. Campos flexiveis usam JSON. Alembic versiona o schema; mudancas
persistentes exigem uma revisao. Foreign keys sao ativadas em cada conexao.

## Entidades e relacoes

- `users`: identidade, papel, estado, perfil, preferencias, `telegram_chat_id`
  privado e versao do token de reset.
- `auth_sessions`: sessao revogavel por utilizador, hash do refresh atual,
  validade, ultimo uso e data de revogacao.
- `organizations`: proprietario, slug, plano e limites. Pode agrupar eventos,
  mas o fluxo de gestao ainda nao tem API propria.
- `events`: organizador, datas, estado, configuracao de equipas e conteudo
  flexivel. Agrega desafios, equipas, projetos e certificados.
- `teams`: pertence a um evento, tem lider e codigo de convite unico.
- `team_members`: liga utilizador e equipa, com papel `leader|member` e estado
  `pending|accepted|rejected`.
- `challenge_categories`: agrupam desafios e criterios dentro de um evento.
- `challenges`: pertencem a evento e categoria.
- `criteria`: pertencem a categoria e definem `max_score` e `weight`.
- `projects`: um projeto por equipa, associado a evento e opcionalmente a
  desafio; estado `draft|submitted|finalized`.
- `project_technologies`: tecnologias unicas por projeto; o fluxo tambem usa
  `projects.tech_stack` em JSON.
- `evaluations`: uma avaliacao por projeto/jurado, com total ponderado.
- `evaluation_scores`: um valor por criterio em cada avaliacao.
- `notifications`: mensagem por utilizador, canal, categoria e estado de leitura.
- `certificates`: um certificado por utilizador/evento/tipo, codigo publico,
  QR code, hash autenticado e snapshot de dados em JSON.

## Invariantes materializadas

- Datas do evento e tamanhos de equipa validos por `CHECK`.
- Nome de equipa unico por evento e membro unico por equipa/utilizador.
- Um projeto por equipa e tecnologia unica por projeto.
- Uma avaliacao por projeto/jurado e um score por criterio/avaliacao.
- Score nao negativo; criterio com maximo e peso positivos.
- Nome de categoria unico por evento e nome de criterio unico por categoria.
- Um certificado por utilizador/evento/tipo.

## Invariantes de dominio

- Um utilizador so pode pertencer a uma equipa aceite por evento.
- So o lider cria, edita ou submete o projeto da equipa.
- Recursos em rotas aninhadas devem pertencer ao `event_id` da rota.
- Criterios de avaliacao devem pertencer ao evento e, quando ha desafio, a
  categoria desse desafio; scores nao podem exceder `max_score`.
- Apenas o dono marca a sua notificacao como lida.
- Organizadores gerem apenas os proprios eventos; admins podem gerir todos.

As regras que cruzam varias tabelas continuam protegidas nos servicos e dentro
da transacao. Ao migrar para outra base, reavaliar concorrencia e isolamento.
