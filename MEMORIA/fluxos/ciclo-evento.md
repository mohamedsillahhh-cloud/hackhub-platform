# Ciclo de evento, equipa, projeto e avaliacao

## Evento

Um organizer/admin cria o evento em `draft`. O organizador dono ou um admin
pode editar, apagar e avancar estados. Transicoes validas:

`draft -> published -> in_progress -> closed`

`published -> draft` tambem e permitido. Nao existe estado `cancelled`.

Categorias, desafios e criterios sao geridos no detalhe do dashboard. O detalhe
publico apresenta esses dados e as equipas reais, com estados vazios honestos.

## Equipa

Participantes criam ou entram numa equipa do evento. Criar equipa torna o
criador lider e membro aceite. Entrada por codigo e aceitacao de convite
verificam lotacao e impedem outra equipa aceite no mesmo evento. O codigo de
convite so aparece em respostas privadas para membros.

Convites persistem um `team_member` pendente e uma notificacao com `member_id`;
o destinatario pode aceitar ou recusar na notificacao. O lider pode remover
membros ou transferir a lideranca para um membro aceite. So depois pode sair.

## Projeto

O lider cria um unico projeto para a equipa. Se escolher desafio, ele deve
pertencer ao mesmo evento. Projetos podem ser editados ate `finalized`; a
submissao muda o estado para `submitted` e regista a data.

## Avaliacao e ranking

Jurados e admins avaliam projetos `submitted|finalized`. Cada criterio e
validado contra o evento/categoria e a pontuacao maxima. O total e a soma de
`score * weight`. O ranking ordena projetos pela media dos totais e inclui a
quantidade de avaliacoes.

Uma avaliacao invalida o cache Redis do evento. Sem Redis, o ranking consulta a
base diretamente. O stream SSE recalcula e envia o ranking periodicamente.

## Certificado

Depois do evento, o servico gera no maximo um certificado por
utilizador/evento/tipo. O snapshot e autenticado com segredo do servidor, o QR
aponta para a rota publica configurada por `APP_URL`, e o download protegido
produz PDF. A verificacao publica recalcula o hash antes de aceitar o codigo.
