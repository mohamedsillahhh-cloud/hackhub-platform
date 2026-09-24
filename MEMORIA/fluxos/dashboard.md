# Fluxo do dashboard

## Matriz de acesso

- `GET /api/v1/dashboard/public-stats` e publico e devolve apenas contagens
  agregadas de eventos visiveis, projetos, equipas e participantes.
- `GET /api/v1/dashboard/stats` exige papel `organizer` ou `admin`.
- Admins recebem metricas globais.
- Organizadores recebem metricas, tecnologias e eventos recentes limitados aos
  eventos de que sao proprietarios.
- Participantes e jurados sao enviados para `/events`; o frontend nao inicia a
  query protegida para estes papeis.

## Gestao de eventos

- A pagina `/dashboard/events` usa `GET /api/v1/events/managed`.
- Para organizadores, a listagem contem apenas eventos proprios.
- Para admins, a listagem contem todos os eventos.
- A listagem publica `/api/v1/events` nao deve ser usada como fonte da area de
  gestao.

## Frontend

- A homepage usa exclusivamente `public-stats`.
- Queries do dashboard nao repetem respostas HTTP 4xx; apenas erros de rede ou
  do servidor podem ser repetidos de forma limitada.
- Apos login, admins e organizadores seguem para `/dashboard`; participantes e
  jurados seguem para `/events`.
