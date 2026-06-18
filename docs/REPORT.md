# RELATÓRIO TÉCNICO DO PROJETO HACKHUB

> **Versão:** 1.0.0
> **Data:** Junho 2026
> **Autor:** Tech Lead / Software Architect
> **Classificação:** Documento Interno — Equipa de Desenvolvimento

---

## Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Módulos do Sistema](#3-módulos-do-sistema)
4. [Fluxo Completo do Sistema](#4-fluxo-completo-do-sistema)
5. [Base de Dados (Modelo Conceitual)](#5-base-de-dados-modelo-conceitual)
6. [API (Design Conceitual)](#6-api-design-conceitual)
7. [Estrutura Completa de Pastas](#7-estrutura-completa-de-pastas)
8. [Explicação de Cada Ficheiro](#8-explicação-de-cada-ficheiro)
9. [Regras de Engenharia](#9-regras-de-engenharia)
10. [Comentários no Código](#10-comentários-no-código)

---

## 1. Visão Geral do Projeto

### O que é o HackHub?

O **HackHub** é uma plataforma open-source profissional para organização e gestão de hackathons, competições tecnológicas, maratonas de programação, feiras de inovação e eventos universitários.

### Problema que resolve

Atualmente, organizar um hackathon envolve múltiplas ferramentas desconectadas:

| Problema | Solução HackHub |
|----------|-----------------|
| Inscrições manuais ou em Google Forms | Sistema de registo e inscrição integrado |
| Formação de equipas desorganizada | Algoritmo inteligente de sugestão de equipas |
| Submissão de projetos por email | Portal centralizado de submissão |
| Avaliação em Excel/planilhas | Sistema de avaliação por critérios com pesos |
| Ranking manual e desatualizado | Ranking em tempo real com SSE |
| Certificados feitos um a um | Geração automática de PDF com QR Code |
| Comunicação fragmentada | Notificações multicanal (email, Telegram, push) |

### Público-alvo

- **Organizadores** — Universidades, comunidades tech, empresas
- **Participantes** — Estudantes, developers, designers, innovators
- **Jurados** — Profissionais que avaliam projetos
- **Administradores** — Gestores da plataforma

### Stack Tecnológica

```
Frontend:   Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui + TanStack Query + Zustand + Framer Motion
Backend:    FastAPI + Python 3.12 + SQLAlchemy 2.0 + Alembic
Base Dados: PostgreSQL 16 + Redis 7
DevOps:     Docker + Docker Compose + Nginx + GitHub Actions
```

---

## 2. Arquitetura do Sistema

### 2.1 Visão Geral da Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                      CLIENTE (Browser)                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │               Next.js 14 (App Router)                     │    │
│  │                                                          │    │
│  │  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌───────────┐  │    │
│  │  │  Pages  │  │Components│  │  Hooks │  │   Store   │  │    │
│  │  │ (SSR/SSG)│  │ (shadcn) │  │(Query) │  │ (Zustand) │  │    │
│  │  └────┬────┘  └──────────┘  └────┬───┘  └───────────┘  │    │
│  │       │                          │                      │    │
│  │       └──────────┬───────────────┘                      │    │
│  │                  │                                      │    │
│  │        ┌─────────▼────────┐                             │    │
│  │        │   API Client     │                             │    │
│  │        │   (Axios)        │                             │    │
│  │        └─────────┬────────┘                             │    │
│  └──────────────────┼──────────────────────────────────────┘    │
│                     │ HTTP/WebSocket                            │
└─────────────────────┼───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                        │
│  - Load Balancing    - SSL Termination    - Rate Limiting      │
│  - CORS Headers      - WebSocket Proxy    - Static Cache       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    FASTAPI (Backend)                            │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐ │
│  │ Endpoints│  │ Services │  │  Repos   │  │  Models/ORM    │ │
│  │  (REST)  │──▶(Business)│──▶ (Data)   │──▶ (SQLAlchemy)  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┬───────┘ │
│                                                     │         │
│  ┌──────────────────────────────────────────────────┼────────┐ │
│  │              Serviços Auxiliares                 │        │ │
│  │  ┌────────┐ ┌──────────┐ ┌─────────┐ ┌───────┐  │        │ │
│  │  │  Auth  │ │   AI     │ │ Notify  │ │Cache  │  │        │ │
│  │  │ (JWT)  │ │(OpenAI)  │ │(Email/  │ │(Redis)│  │        │ │
│  │  └────────┘ └──────────┘ └─────────┘ └───────┘  │        │ │
│  └──────────────────────────────────────────────────┼────────┘ │
│                                                     │         │
└─────────────────────────────────────────────────────┼──────────┘
                                                       │
                    ┌──────────────────────────────────┼──────────┐
                    │              Redis               │          │
                    │  ┌────────┐ ┌──────────┐         │          │
                    │  │  Cache │ │  Pub/Sub │         │          │
                    │  │ (Session│ │ (Real-time│        │          │
                    │  │  Data) │ │  Ranking) │         │          │
                    │  └────────┘ └──────────┘         │          │
                    └─────────────────────────────────────────────┘
                                                       │
                    ┌──────────────────────────────────▼──────────┐
                    │           PostgreSQL 16                      │
                    │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
                    │  │  Users   │ │  Events  │ │  Teams   │    │
                    │  │  Projects│ │Evaluations│ │Certificates│   │
                    │  └──────────┘ └──────────┘ └──────────┘    │
                    └─────────────────────────────────────────────┘
```

### 2.2 Arquitetura Frontend (Next.js 14 App Router)

O frontend utiliza o **App Router** do Next.js 14, que é o novo sistema de routing baseado em ficheiros e pastas.

**Como funciona o App Router:**

```
src/app/
├── page.tsx           → Rota: /
├── layout.tsx         → Layout principal (envolve todas as páginas)
├── events/
│   ├── page.tsx       → Rota: /events
│   └── [id]/
│       └── page.tsx   → Rota: /events/:id
└── dashboard/
    └── page.tsx       → Rota: /dashboard
```

**Responsabilidades de cada camada no frontend:**

| Camada | Tecnologia | Responsabilidade |
|--------|-----------|-----------------|
| **Pages** | Next.js App Router | Renderização, SSR/SSG, metadata, SEO |
| **Layouts** | React Components | Estrutura global (Navbar, Footer, Sidebar) |
| **Components** | shadcn/ui + Tailwind | UI reutilizável, acessível, responsiva |
| **Hooks** | TanStack Query | Data fetching, caching, mutations, polling |
| **Store** | Zustand | Estado global (auth tokens, tema) |
| **API Client** | Axios | Chamadas HTTP, interceptors, refresh token |

**Estratégia de renderização:**

- **Páginas públicas** (landing, eventos públicos) → Static Generation (SSG)
- **Páginas de listagem** (eventos, equipas) → Server-Side Rendering (SSR) incremental
- **Páginas de detalhe** (evento, equipa, projeto) → SSR com cache
- **Dashboards** → Client-Side Rendering (CSR) com autenticação
- **Componentes interativos** — Todos client-side com `'use client'`

### 2.3 Arquitetura Backend (FastAPI + Clean Architecture)

O backend segue **Clean Architecture** com 3 camadas principais:

```
┌─────────────────────────────────────────────────┐
│                API Layer                         │
│  (Endpoints/Routers)                             │
│  └── Recebe request, valida input,              │
│      chama service, retorna response            │
├─────────────────────────────────────────────────┤
│                Service Layer                     │
│  (Business Logic)                                │
│  └── Regras de negócio, orquestração,           │
│      cálculos, autorização                      │
├─────────────────────────────────────────────────┤
│              Repository Layer                    │
│  (Data Access)                                   │
│  └── Consultas SQL, CRUD, agregações            │
├─────────────────────────────────────────────────┤
│              Database Layer                      │
│  (SQLAlchemy ORM)                                │
│  └── Models, migrations, conexão                │
└─────────────────────────────────────────────────┘
```

**Porque 3 camadas?**

- **Separação de responsabilidades** — Cada camada tem um trabalho específico
- **Testabilidade** — Podemos testar cada camada isoladamente
- **Manutenibilidade** — Mudar a base de dados não afeta a lógica de negócio
- **Reutilização** — Services podem ser usados por múltiplos endpoints

### 2.4 Comunicação Frontend-Backend

```
Frontend                          Backend
   │                                 │
   │  1. HTTP Request (Axios)        │
   │  ───────────────────────────────▶│
   │                                 │
   │  2. JWT Token (Authorization)   │
   │  ───────────────────────────────▶│
   │                                 │
   │  3. Validação + Processamento   │
   │                                 │
   │  4. HTTP Response (JSON)        │
   │  ◀───────────────────────────────│
   │                                 │
   │  5. SSE/WebSocket (Ranking)     │
   │  ◀───────────────────────────────│
```

**Tipos de comunicação:**

1. **REST API (HTTP)** — Operações CRUD padrão (JSON)
2. **Server-Sent Events (SSE)** — Ranking em tempo real (unidirecional)
3. **WebSocket** — Notificações em tempo real (bidirecional, futuro)

### 2.5 Sistema de Autenticação

O HackHub usa **JWT (JSON Web Tokens)** com dois tipos de tokens:

```
┌──────────────────────────────────────────────┐
│              FLUXO DE AUTENTICAÇÃO            │
├──────────────────────────────────────────────┤
│                                               │
│  1. Utilizador faz login                      │
│     (email + password)                       │
│         │                                     │
│         ▼                                     │
│  2. Backend verifica credenciais              │
│         │                                     │
│         ▼                                     │
│  3. Backend gera 2 tokens:                    │
│     ┌────────────────────┐                   │
│     │ Access Token       │ 15 min            │
│     │ (curta duração)    │                   │
│     └─────────┬──────────┘                   │
│               │                              │
│     ┌─────────▼──────────┐                   │
│     │ Refresh Token      │ 7 dias            │
│     │ (longa duração)    │                   │
│     └────────────────────┘                   │
│         │                                     │
│         ▼                                     │
│  4. Frontend guarda tokens (localStorage)     │
│         │                                     │
│         ▼                                     │
│  5. Cada request envia Access Token           │
│     no header: Authorization: Bearer <token> │
│         │                                     │
│         ▼                                     │
│  6. Quando Access Token expira:               │
│     → Frontend usa Refresh Token             │
│     → Backend emite novo Access Token        │
│     → Sem necessidade de novo login          │
│                                               │
└──────────────────────────────────────────────┘
```

**Roles e Permissões:**

| Role | Descrição | Ações Principais |
|------|-----------|------------------|
| `ADMIN` | Acesso total | Gerir tudo, aprovar eventos, ver stats globais |
| `ORGANIZER` | Cria eventos | Criar/editar eventos, gerir inscrições, criar desafios |
| `JUDGE` | Avalia projetos | Atribuir notas, deixar comentários, ver projetos |
| `PARTICIPANT` | Participa | Inscrever-se, criar equipa, submeter projetos |

### 2.6 Sistema de Eventos (Máquina de Estados)

Cada evento percorre um ciclo de vida bem definido:

```
        ┌──────────┐
        │  DRAFT   │  ← Estado inicial (só o organizador vê)
        └────┬─────┘
             │ Publicar
             ▼
        ┌──────────┐
        │ PUBLISHED│  ← Visível para todos, inscrições abertas
        └────┬─────┘
             │ Iniciar
             ▼
        ┌───────────┐
        │ IN_PROGRESS│ ← Submissões abertas, avaliação a decorrer
        └────┬──────┘
             │ Encerrar
             ▼
        ┌──────────┐
        │  CLOSED  │  ← Estado final, apenas leitura
        └──────────┘
```

**Regras de transição:**

- `DRAFT → PUBLISHED`: Apenas o organizador ou admin
- `PUBLISHED → IN_PROGRESS`: Quando o evento começa (data) ou manualmente
- `IN_PROGRESS → CLOSED`: Quando o evento termina ou manualmente
- **Não pode voltar** a estados anteriores (imutabilidade do histórico)

---

## 3. Módulos do Sistema

### 3.1 Módulo de Autenticação

#### Responsabilidade
Gerir registo, login, logout, verificação de email, recuperação de password e refresh de tokens.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `POST` | `/api/v1/auth/register` | Registar novo utilizador |
| `POST` | `/api/v1/auth/login` | Login (devolve access + refresh tokens) |
| `POST` | `/api/v1/auth/refresh` | Renovar access token |
| `POST` | `/api/v1/auth/verify-email/{token}` | Verificar email |
| `POST` | `/api/v1/auth/password-reset` | Solicitar reset de password |
| `POST` | `/api/v1/auth/password-reset/confirm` | Confirmar reset |
| `GET` | `/api/v1/auth/me` | Obter perfil do utilizador atual |
| `PUT` | `/api/v1/auth/me` | Atualizar perfil |

#### Regras de Negócio

- Email e username devem ser únicos
- Password deve ter no mínimo 8 caracteres, com maiúscula, minúscula e número
- Access token expira em 15 minutos (configurável)
- Refresh token expira em 7 dias
- Conta não verificada por email tem acesso limitado
- Rate limiting: 5 tentativas de login por minuto

#### Ficheiros Relacionados

| Ficheiro | Função |
|----------|--------|
| `backend/app/core/security.py` | Criação e validação de JWT, hashing de passwords |
| `backend/app/services/auth_service.py` | Lógica de autenticação |
| `backend/app/api/v1/endpoints/auth.py` | Rotas de autenticação |

---

### 3.2 Módulo de Utilizadores

#### Responsabilidade
Gerir perfis de utilizador, skills, experiência, preferências e estatísticas.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `GET` | `/api/v1/users` | Listar utilizadores (admin) |
| `GET` | `/api/v1/users/{id}` | Ver perfil público |
| `GET` | `/api/v1/users/{id}/certificates` | Ver certificados do utilizador |
| `GET` | `/api/v1/dashboard/stats` | Estatísticas globais (admin) |

#### Regras de Negócio

- Perfil público: nome, bio, universidade, curso, skills, GitHub, LinkedIn
- Perfil privado: email, dados de autenticação
- Utilizadores podem pesquisar outros por skills, universidade, país
- Admin pode ver estatísticas de toda a plataforma

#### Campos do Perfil

```
full_name: string
bio: text              → Pequena descrição do utilizador
university: string     → Universidade de origem
course: string         → Curso/faculdade
country: string        → País
skills: string[]       → ["Python", "React", "Docker"]
github_url: string     → Link do GitHub
linkedin_url: string   → Link do LinkedIn
portfolio_url: string  → Link do portfólio
experience_level: string → beginner | intermediate | advanced | expert
preferred_languages: string[] → ["Python", "JavaScript", "Go"]
preferred_frameworks: string[] → ["React", "FastAPI", "Next.js"]
interest_areas: string[] → ["IA", "DevOps", "Frontend"]
```

---

### 3.3 Módulo de Eventos

#### Responsabilidade
Criar, gerir e monitorizar eventos/hackathons.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `GET` | `/api/v1/events` | Listar eventos (com filtros) |
| `POST` | `/api/v1/events` | Criar evento |
| `GET` | `/api/v1/events/{id}` | Detalhes do evento |
| `PUT` | `/api/v1/events/{id}` | Atualizar evento |
| `DELETE` | `/api/v1/events/{id}` | Apagar evento |
| `PATCH` | `/api/v1/events/{id}/status` | Mudar estado do evento |

#### Regras de Negócio

- Só organizadores e admins podem criar eventos
- Evento em draft é invisível para participantes
- Data de início deve ser posterior à data atual
- Data de fim deve ser posterior à data de início
- Cada evento tem configuração própria de tamanho de equipa (min/max)
- Só é possível inscrever-se em eventos com status `published`

#### Campos do Evento

```
title: string          → Nome do evento
description: text      → Descrição detalhada
cover_image: string    → URL da imagem de capa
start_date: datetime   → Data de início
end_date: datetime     → Data de fim
location: string       → Local físico ou "Online"
is_online: boolean     → Indica se é online
regulations: text      → Regulamento completo
schedule: json         → Cronograma (array de eventos)
sponsors: json         → Patrocinadores (nome, logo, site)
prizes: json           → Prémios (posição, descrição)
faq: json              → Perguntas frequentes
max_team_size: int     → Máximo de membros por equipa
min_team_size: int     → Mínimo de membros por equipa
```

---

### 3.4 Módulo de Equipas

#### Responsabilidade
Gestão de equipas: criação, convites, membros, liderança.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `GET` | `/api/v1/events/{id}/teams` | Listar equipas do evento |
| `POST` | `/api/v1/events/{id}/teams` | Criar equipa |
| `GET` | `/api/v1/events/{id}/teams/{team_id}` | Detalhes da equipa |
| `POST` | `/api/v1/events/{id}/teams/{team_id}/invite` | Convidar membro |
| `POST` | `/api/v1/events/{id}/teams/join` | Entrar na equipa por código |
| `POST` | `/api/v1/events/{id}/teams/{team_id}/accept/{member_id}` | Aceitar membro |
| `DELETE` | `/api/v1/events/{id}/teams/{team_id}/leave` | Sair da equipa |
| `DELETE` | `/api/v1/events/{id}/teams/{team_id}/members/{member_id}` | Remover membro |

#### Regras de Negócio

- Cada participante só pode estar numa equipa por evento
- Líder da equipa pode convidar, aceitar, rejeitar e remover membros
- Código de convite é único e expira após uso
- Tamanho mínimo/máximo da equipa é definido pelo evento
- Para submeter projetos, a equipa precisa ter o mínimo de membros
- Mudar de líder requer aprovação do novo líder

#### Fluxo de Convite

```
1. Líder clica "Convidar Membro"
2. Sistema gera código único (ex: "TEAM-A3B7")
3. Líder partilha código com o participante
4. Participante entra com o código
5. Líder aceita ou rejeita a entrada
6. Participante é adicionado à equipa
```

---

### 3.5 Módulo de Submissões (Projetos)

#### Responsabilidade
Permitir que equipas submetam e atualizem os seus projetos.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `GET` | `/api/v1/events/{id}/projects` | Listar projetos do evento |
| `POST` | `/api/v1/events/{id}/projects` | Submeter projeto |
| `GET` | `/api/v1/events/{id}/projects/{project_id}` | Detalhes do projeto |
| `PUT` | `/api/v1/events/{id}/projects/{project_id}` | Atualizar projeto |
| `POST` | `/api/v1/events/{id}/projects/{project_id}/submit` | Finalizar submissão |

#### Regras de Negócio

- Só a equipa pode submeter/editar o seu projeto
- Múltiplas atualizações permitidas até ao encerramento do evento
- Estado `draft` → projeto em edição (não submetido)
- Estado `submitted` → projeto pronto para avaliação
- Estado `finalized` → projeto final (não pode ser editado)
- Projeto pode estar associado a um desafio específico

#### Campos do Projeto

```
name: string              → Nome do projeto
description: text         → Descrição do projeto
github_url: string        → Repositório GitHub
demo_video_url: string    → Link do vídeo de demonstração
presentation_url: string  → Link da apresentação (PDF/Google Slides)
tech_stack: string[]      → Tecnologias utilizadas
challenge_id: uuid (opt.) → Desafio associado
```

---

### 3.6 Módulo de Avaliação

#### Responsabilidade
Permitir que jurados avaliem projetos por critérios configuráveis.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `POST` | `/api/v1/events/{id}/evaluations` | Submeter avaliação (jurado) |
| `GET` | `/api/v1/events/{id}/evaluations/projects/{project_id}` | Avaliações de um projeto |
| `GET` | `/api/v1/events/{id}/evaluations/ranking` | Ranking do evento |
| `GET` | `/api/v1/events/{id}/evaluations/my` | Minhas avaliações (jurado) |

#### Regras de Negócio

- Só utilizadores com role `judge` podem avaliar
- Cada critério tem um peso configurável (ex: Inovação: peso 2, Técnica: peso 1)
- A nota final é a média ponderada de todos os critérios
- Cada jurado avalia cada projeto uma vez (não pode reavaliar)
- O ranking é calculado automaticamente com base nas avaliações
- Critérios de desempate: inovação > técnica > design

#### Sistema de Pontuação

```
Fórmula da nota final:

  Nota Final = Σ (score_criterio × peso_criterio) / Σ pesos

Exemplo:
  Inovação:  8/10  × peso 2 = 16
  Impacto:   7/10  × peso 1 = 7
  Técnica:   9/10  × peso 2 = 18
  Design:    7/10  × peso 1 = 7
  Apresentação: 8/10 × peso 1 = 8

  Total: (16 + 7 + 18 + 7 + 8) / (2 + 1 + 2 + 1 + 1) = 56 / 7 = 8.0
```

---

### 3.7 Módulo de Ranking

#### Responsabilidade
Calcular e disponibilizar a classificação em tempo real.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `GET` | `/api/v1/events/{id}/ranking` | Obter ranking completo |
| `GET` | `/api/v1/events/{id}/ranking/stream` | SSE com atualizações em tempo real |

#### Regras de Negócio

- Ranking ordenado por nota total (decrescente)
- Critério de desempate: inovação > impacto > técnica > design
- Ranking é recalculado automaticamente após cada avaliação
- Cache em Redis para consultas rápidas
- SSE (Server-Sent Events) para atualizações em tempo real no frontend
- Top 3 destacados com medalhas (ouro, prata, bronze)

#### Como o SSE funciona

```
1. Frontend abre conexão SSE com /ranking/stream
2. Backend mantém conexão aberta
3. Quando uma avaliação é submetida:
   a. Backend recalcula ranking
   b. Envia novo ranking através da conexão SSE
4. Frontend recebe e atualiza a UI sem refresh
5. Conexão é automática e recomeça se cair
```

---

### 3.8 Módulo de Notificações

#### Responsabilidade
Enviar notificações para utilizadores através de múltiplos canais.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `GET` | `/api/v1/notifications` | Listar notificações do utilizador |
| `PUT` | `/api/v1/notifications/{id}/read` | Marcar como lida |
| `PUT` | `/api/v1/notifications/read-all` | Marcar todas como lidas |

#### Tipos de Notificação

| Categoria | Quando acontece | Canal |
|-----------|----------------|-------|
| `team_invite` | Convite para equipa | Email + Telegram |
| `registration_approved` | Inscrição aprovada | Email |
| `new_challenge` | Novo desafio publicado | Email + Push |
| `result_published` | Resultados disponíveis | Email + Telegram |

#### Regras de Negócio

- Notificações são guardadas na base de dados
- Cada notificação pode ser enviada por múltiplos canais
- Email é o canal obrigatório (padrão)
- Telegram é opcional (configurável pelo utilizador)
- Push notifications são o canal premium (futuro)
- Notificações não lidas têm um badge no frontend
- Polling a cada 30 segundos para verificar novas notificações

---

### 3.9 Módulo de IA (Inteligência Artificial)

#### Responsabilidade
Fornecer funcionalidades inteligentes usando OpenAI.

#### Endpoints Principais

| Método | Rota | Funcionalidade |
|--------|------|---------------|
| `POST` | `/api/v1/ai/events/{id}/ask` | Assistente do evento (FAQ) |
| `POST` | `/api/v1/ai/evaluate/{project_id}` | Avaliação assistida por IA |
| `POST` | `/api/v1/ai/events/{id}/suggest-teams` | Sugestão de equipas |

#### Funcionalidades de IA

**1. Assistente do Evento**
```
Input:  "Qual o prazo de submissão?"
Processo:
  → Busca dados do evento (FAQ, schedule, regulamento)
  → Envia contexto + pergunta para OpenAI
  → OpenAI gera resposta baseada no contexto
Output: "O prazo de submissão é 20 de Junho às 23:59 UTC"
```

**2. Avaliação Assistida**
```
Input:  Projeto ID
Processo:
  → Busca dados do projeto (README, descrição, tech stack)
  → Envia para OpenAI com prompt de avaliação
  → OpenAI analisa: inovação, complexidade técnica, impacto
Output: "O projeto demonstra forte inovação... Recomendação: 85/100"
```

**3. Sugestão de Equipas**
```
Input:  Evento ID
Processo:
  → Busca todos os participantes com skills
  → Algoritmo de matching:
     - Participante com Python + IA
     - Participante com React + UI
     - Participante com DevOps
     → Equipa equilibrada! ✅
Output: Lista de equipas sugeridas com membros
```

#### Regras de Negócio

- IA requer chave da OpenAI configurada (senão, responde com fallback)
- Assistente do evento usa apenas dados do evento (não alucina)
- Avaliação assistida é uma sugestão, não substitui o jurado humano
- Sugestão de equipas usa algoritmo de weighted matching
- Custos de API da OpenAI devem ser monitorizados

---

## 4. Fluxo Completo do Sistema

### 4.1 Fluxo do Participante

```
PARTICIPANTE ABRE O SITE
         │
         ▼
  ┌──────────────────┐
  │  Landing Page    │
  │  - Hero section  │
  │  - Features      │
  │  - Stats         │
  │  - CTA           │
  └───────┬──────────┘
          │ Clica "Get Started"
          ▼
  ┌──────────────────┐
  │  Register Page   │
  │  - Nome completo │
  │  - Email         │
  │  - Username      │
  │  - Password      │
  │  → Validação     │
  └───────┬──────────┘
          │ Submete formulário
          ▼
  ┌──────────────────┐
  │  Backend:        │
  │  1. Valida dados │
  │  2. Hash password│
  │  3. Cria user    │
  │  4. Envia email  │
  │     verificação  │
  └───────┬──────────┘
          │
          ▼
  ┌──────────────────┐
  │  Verifica email  │
  │  → Clica link    │
  └───────┬──────────┘
          │
          ▼
  ┌──────────────────┐
  │  Login Page      │
  │  - Email         │
  │  - Password      │
  └───────┬──────────┘
          │
          ▼
  ┌───────────────────────────────────┐
  │  Backend:                         │
  │  1. Verifica credenciais          │
  │  2. Gera access_token (15min)     │
  │  3. Gera refresh_token (7dias)    │
  │  4. Devolve tokens                │
  └──────────────┬────────────────────┘
                 │
                 ▼
  ┌──────────────────┐
  │  Dashboard       │
  │  - Eventos       │
  │  - Minhas equipas│
  │  - Notificações  │
  └───────┬──────────┘
          │
          ▼
  ┌──────────────────┐
  │  Events Page     │
  │  - Lista eventos │
  │  - Filtros       │
  │  - Pesquisa      │
  └───────┬──────────┘
          │ Clica num evento
          ▼
  ┌──────────────────────────────┐
  │  Event Detail Page           │
  │  - Informação do evento     │
  │  - Cronograma               │
  │  - Desafios                 │
  │  - Equipas                  │
  │  - Ranking                  │
  │  - FAQ                      │
  └───────┬──────────────────────┘
          │ Clica "Participar"
          ▼
  ┌─────────────────────────────────┐
  │  Escolhe: Criar ou Entrar      │
  │  na Equipa                      │
  │                                  │
  │  ┌──────────┐  ┌─────────────┐  │
  │  │Criar     │  │Entrar com   │  │
  │  │Equipa    │  │Código       │  │
  │  └────┬─────┘  └──────┬──────┘  │
  └───────┼───────────────┼─────────┘
          │               │
          ▼               ▼
  ┌──────────────┐  ┌─────────────────┐
  │ Cria equipa  │  │ Insere código   │
  │ - Nome       │  │ + Líder aceita │
  │ - Descrição  │  └─────────────────┘
  └──────┬───────┘
         │
         ▼
  ┌─────────────────────────┐
  │  Team Page              │
  │  - Membros              │
  │  - Convidar membros     │
  │  - Submeter projeto    │
  └──────────┬──────────────┘
             │
             ▼
  ┌─────────────────────┐
  │  Submeter Projeto   │
  │  - Nome             │
  │  - Descrição        │
  │  - GitHub URL       │
  │  - Vídeo demo       │
  │  - Tech stack       │
  └──────────┬──────────┘
             │ Submete
             ▼
  ┌──────────────────┐
  │  Projeto         │
  │  → Draft         │
  │  → Pode editar   │
  │  → "Finalizar"   │
  └───────┬──────────┘
          │ Finaliza
          ▼
  ┌──────────────────┐
  │  Projeto         │
  │  → Submitted     │
  │  → Aguarda       │
  │    avaliação     │
  └───────┬──────────┘
          │
          ▼
  ┌───────────────────────────────────┐
  │  Jurados avaliam (módulo 3.6)    │
  │  → Cada critério com peso       │
  │  → Nota final calculada          │
  └──────────────┬────────────────────┘
                 │
                 ▼
  ┌──────────────────────────┐
  │  Ranking atualizado      │
  │  em tempo real (SSE)     │
  │                          │
  │  🥇 1º Melhor Projeto   │
  │  🥈 2º Segundo Lugar    │
  │  🥉 3º Terceiro Lugar   │
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────┐
  │  Certificado     │
  │  → PDF gerado    │
  │  → QR Code       │
  │  → Download      │
  └──────────────────┘
```

### 4.2 Fluxo do Organizador

```
ORGANIZADOR FAZ LOGIN
         │
         ▼
  ┌──────────────────┐
  │  Dashboard       │
  │  - Criar Evento  │
  │  - Gerir Eventos │
  │  - Stats         │
  └───────┬──────────┘
          │ Clica "Criar Evento"
          ▼
  ┌──────────────────┐
  │  Event Form      │
  │  → Preenche tudo │
  │  → Salva (Draft) │
  └───────┬──────────┘
          │
          ▼
  ┌──────────────────┐
  │  Publica Evento  │
  │  → Draft→Published│
  └───────┬──────────┘
          │
          ▼
  ┌───────────────────────────────┐
  │  Gestão do Evento            │
  │  - Criar Desafios            │
  │  - Definir Critérios         │
  │  - Atribuir Jurados          │
  │  - Acompanhar Submissões     │
  │  - Ver Ranking               │
  │  - Gerar Certificados        │
  └───────────────────────────────┘
```

### 4.3 Fluxo do Jurado

```
JURADO FAZ LOGIN
         │
         ▼
  ┌──────────────────┐
  │  Dashboard       │
  │  - Eventos para  │
  │    avaliar       │
  └───────┬──────────┘
          │
          ▼
  ┌────────────────────────────┐
  │  Lista de Projetos        │
  │  → Cada projeto para      │
  │    avaliar                │
  └───────┬────────────────────┘
          │ Abre projeto
          ▼
  ┌────────────────────────────┐
  │  Formulário de Avaliação  │
  │  - Critério 1: Inovação   │
  │    (peso 2) ████████ 8/10 │
  │  - Critério 2: Técnica    │
  │    (peso 2) ███████ 7/10  │
  │  - Critério 3: Design     │
  │    (peso 1) ████████ 8/10 │
  │  - Comentário: "Bom...    │
  │  → Submeter               │
  └───────┬────────────────────┘
          │
          ▼
  ┌──────────────────┐
  │  Ranking         │
  │  atualizado em   │
  │  tempo real      │
  └──────────────────┘
```

---

## 5. Base de Dados (Modelo Conceitual)

### 5.1 Diagrama Entidade-Relacionamento

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ┌──────────────┐       ┌──────────────┐       ┌──────────────────┐      │
│    │     User     │       │    Event     │       │      Team        │      │
│    ├──────────────┤       ├──────────────┤       ├──────────────────┤      │
│    │ id (PK)      │◄──────│ organizer_id │──┐    │ id (PK)          │      │
│    │ email (UQ)   │       │ id (PK)      │  │    │ name             │      │
│    │ username (UQ)│       │ title        │  │    │ event_id (FK)────┼──┐   │
│    │ full_name    │       │ description  │  │    │ leader_id (FK)───┼──┤   │
│    │ role         │       │ start_date   │  │    │ invitation_code  │  │   │
│    │ is_verified  │       │ end_date     │  │    │ created_at       │  │   │
│    │ skills[]     │       │ status       │  │    └────────┬─────────┘  │   │
│    │ university   │       │ max_team_size│  │             │            │   │
│    │ country      │       │ regulations  │  │             │            │   │
│    └──────────────┘       │ faq          │  │             │            │   │
│          │                │ schedule     │  │   ┌────────▼─────────┐   │   │
│          │                │ prizes       │  │   │   TeamMember    │   │   │
│          │                │ sponsors     │  │   ├──────────────────┤   │   │
│          │                └──────────────┘  │   │ id (PK)         │   │   │
│          │                      │           │   │ team_id (FK)────┼───┘   │
│          │                      │           │   │ user_id (FK)────┼───────┘
│          │                      │           │   │ role            │       │
│          │                      │           │   │ status          │       │
│          │                      │           │   │ invited_by      │       │
│          │                      │           │   └─────────────────┘       │
│          │                      │                                         │
│          │              ┌───────┴──────────┐                              │
│          │              │  Challenge       │                              │
│          │              ├──────────────────┤                              │
│          │              │ id (PK)          │                              │
│          │              │ event_id (FK)────┼───┐                          │
│          │              │ title            │   │                          │
│          │              │ description      │   │                          │
│          │              │ requirements     │   │                          │
│          │              └──────────────────┘   │                          │
│          │                                     │                          │
│          │              ┌─────────────────┐    │                          │
│          │              │ChallengeCategory│    │                          │
│          │              ├─────────────────┤    │                          │
│          │              │ id (PK)         │    │                          │
│          │              │ event_id (FK)───┼────┼──┐                       │
│          │              │ name            │    │  │                       │
│          │              │ order           │    │  │                       │
│          │              └────────┬────────┘    │  │                       │
│          │                       │             │  │                       │
│          │              ┌────────▼────────┐    │  │                       │
│          │              │   Criterion     │    │  │                       │
│          │              ├─────────────────┤    │  │                       │
│          │              │ id (PK)         │    │  │                       │
│          │              │ category_id(FK)─┼────┼──┘                       │
│          │              │ name            │    │                          │
│          │              │ max_score       │    │                          │
│          │              │ weight          │    │                          │
│          │              └─────────────────┘    │                          │
│          │                                     │                          │
│          │              ┌──────────────────┐   │                          │
│          │              │    Project       │   │                          │
│          │              ├──────────────────┤   │                          │
│          │              │ id (PK)          │   │                          │
│          │              │ team_id (FK)─────┼───┼──────────────────────────┘
│          │              │ event_id (FK)────┼───┘                          │
│          │              │ challenge_id(FK) │                               │
│          │              │ name             │                               │
│          │              │ description      │                               │
│          │              │ github_url       │                               │
│          │              │ tech_stack[]     │                               │
│          │              │ status           │                               │
│          │              └────────┬─────────┘                               │
│          │                       │                                         │
│          │              ┌────────▼──────────┐                              │
│          │              │   Evaluation      │                              │
│          │              ├───────────────────┤                              │
│          │              │ id (PK)           │                              │
│          ├──────────────┤ judge_id (FK)     │                              │
│          │              │ project_id (FK)   │                              │
│          │              │ comment           │                              │
│          │              │ total_score       │                              │
│          │              └────────┬──────────┘                              │
│          │                       │                                         │
│          │              ┌────────▼──────────┐                              │
│          │              │ EvaluationScore   │                              │
│          │              ├───────────────────┤                              │
│          │              │ id (PK)           │                              │
│          │              │ evaluation_id(FK) │                              │
│          │              │ criterion_id(FK)  │                              │
│          │              │ score             │                              │
│          │              └───────────────────┘                              │
│          │                                                                 │
│          │              ┌──────────────────┐                               │
│          ├──────────────┤ Notification     │                               │
│          │              ├──────────────────┤                               │
│          │              │ id (PK)          │                               │
│          │              │ user_id (FK) ────┘                               │
│          │              │ type             │                               │
│          │              │ category         │                               │
│          │              │ title            │                               │
│          │              │ message          │                               │
│          │              │ read             │                               │
│          │              └──────────────────┘                               │
│          │                                                                 │
│          │              ┌──────────────────┐                               │
│          ├──────────────┤ Certificate      │                               │
│          │              ├──────────────────┤                               │
│          │              │ id (PK)          │                               │
│          │              │ user_id (FK) ────┘                               │
│          │              │ event_id (FK) ───┐                               │
│          │              │ type             │                               │
│          │              │ qr_code_url      │                               │
│          │              │ verification_code│                               │
│          │              │ digital_signature│                               │
│          │              └──────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Descrição das Tabelas

#### 5.2.1 `users` — Utilizadores da plataforma

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `email` | VARCHAR(255) UNIQUE | Email do utilizador |
| `username` | VARCHAR(100) UNIQUE | Nome de utilizador |
| `hashed_password` | VARCHAR(255) | Password com hash (bcrypt) |
| `full_name` | VARCHAR(255) | Nome completo |
| `role` | ENUM(admin/organizer/judge/participant) | Papel no sistema |
| `is_active` | BOOLEAN | Conta ativa? |
| `is_verified` | BOOLEAN | Email verificado? |
| `avatar_url` | VARCHAR(500) | URL da foto de perfil |
| `bio` | TEXT | Biografia |
| `university` | VARCHAR(255) | Universidade |
| `course` | VARCHAR(255) | Curso |
| `country` | VARCHAR(100) | País |
| `skills` | ARRAY(VARCHAR) | Competências |
| `github_url` | VARCHAR(500) | Link GitHub |
| `linkedin_url` | VARCHAR(500) | Link LinkedIn |
| `portfolio_url` | VARCHAR(500) | Link Portfólio |
| `experience_level` | VARCHAR(50) | Nível de experiência |
| `preferred_languages` | ARRAY(VARCHAR) | Linguagens preferidas |
| `preferred_frameworks` | ARRAY(VARCHAR) | Frameworks preferidas |
| `interest_areas` | ARRAY(VARCHAR) | Áreas de interesse |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Data de atualização |

**Relações:**
- Um `User` pode estar em várias `TeamMember` (N para N através de Team)
- Um `User` pode ter várias `Notification`
- Um `User` pode ter vários `Certificate`
- Um `User` (como jurado) pode fazer várias `Evaluation`

#### 5.2.2 `events` — Eventos/Hackathons

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `title` | VARCHAR(255) | Título do evento |
| `description` | TEXT | Descrição |
| `cover_image` | VARCHAR(500) | Imagem de capa |
| `start_date` | TIMESTAMP | Data de início |
| `end_date` | TIMESTAMP | Data de fim |
| `location` | VARCHAR(255) | Localização |
| `is_online` | BOOLEAN | Evento online? |
| `status` | ENUM(draft/published/in_progress/closed) | Estado |
| `regulations` | TEXT | Regulamento |
| `schedule` | JSONB | Cronograma |
| `sponsors` | JSONB | Patrocinadores |
| `prizes` | JSONB | Prémios |
| `faq` | JSONB | FAQ |
| `max_team_size` | INTEGER | Máx membros/equipa |
| `min_team_size` | INTEGER | Mín membros/equipa |
| `organizer_id` | UUID (FK → users.id) | Organizador |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Data de atualização |

**Relações:**
- Um `Event` pertence a um `User` (organizador)
- Um `Event` pode ter vários `Team`
- Um `Event` pode ter vários `Challenge`
- Um `Event` pode ter vários `Project`
- Um `Event` pode ter vários `Certificate`

#### 5.2.3 `teams` — Equipas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `name` | VARCHAR(255) | Nome da equipa |
| `description` | TEXT | Descrição |
| `event_id` | UUID (FK → events.id) | Evento |
| `leader_id` | UUID (FK → users.id) | Líder da equipa |
| `invitation_code` | VARCHAR(50) UNIQUE | Código de convite |
| `created_at` | TIMESTAMP | Data de criação |

#### 5.2.4 `team_members` — Membros das equipas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `team_id` | UUID (FK → teams.id) | Equipa |
| `user_id` | UUID (FK → users.id) | Utilizador |
| `role` | ENUM(leader/member) | Papel na equipa |
| `status` | ENUM(pending/accepted/rejected) | Estado do convite |
| `invited_by` | UUID (FK → users.id) | Quem convidou |
| `created_at` | TIMESTAMP | Data de entrada |

#### 5.2.5 `projects` — Projetos submetidos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `team_id` | UUID (FK → teams.id) | Equipa |
| `event_id` | UUID (FK → events.id) | Evento |
| `challenge_id` | UUID (FK → challenges.id) NULL | Desafio associado |
| `name` | VARCHAR(255) | Nome do projeto |
| `description` | TEXT | Descrição |
| `github_url` | VARCHAR(500) | Repositório |
| `demo_video_url` | VARCHAR(500) | Vídeo demo |
| `presentation_url` | VARCHAR(500) | Apresentação |
| `tech_stack` | ARRAY(VARCHAR) | Tecnologias |
| `status` | ENUM(draft/submitted/finalized) | Estado |
| `submitted_at` | TIMESTAMP | Data de submissão |

#### 5.2.6 `evaluations` — Avaliações

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `project_id` | UUID (FK → projects.id) | Projeto avaliado |
| `judge_id` | UUID (FK → users.id) | Jurado |
| `comment` | TEXT | Comentário |
| `total_score` | FLOAT | Nota final calculada |
| `submitted_at` | TIMESTAMP | Data da avaliação |

#### 5.2.7 `evaluation_scores` — Pontuações por critério

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `evaluation_id` | UUID (FK → evaluations.id) | Avaliação |
| `criterion_id` | UUID (FK → criteria.id) | Critério |
| `score` | FLOAT | Nota |

#### 5.2.8 `notifications` — Notificações

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `user_id` | UUID (FK → users.id) | Destinatário |
| `type` | ENUM(email/telegram/push) | Canal |
| `category` | ENUM(...) | Categoria |
| `title` | VARCHAR(255) | Título |
| `message` | TEXT | Mensagem |
| `data` | JSONB NULL | Dados adicionais |
| `read` | BOOLEAN | Lida? |
| `sent_at` | TIMESTAMP | Enviada em |
| `read_at` | TIMESTAMP | Lida em |

#### 5.2.9 `certificates` — Certificados

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID (PK) | Identificador único |
| `user_id` | UUID (FK → users.id) | Utilizador |
| `event_id` | UUID (FK → events.id) | Evento |
| `type` | ENUM(participation/finalist/winner/judge/organizer) | Tipo |
| `template_name` | VARCHAR(100) | Template usado |
| `qr_code_url` | VARCHAR(500) | URL do QR Code |
| `verification_code` | VARCHAR(100) UNIQUE | Código de verificação |
| `digital_signature` | TEXT | Assinatura digital |
| `issued_at` | TIMESTAMP | Data de emissão |

### 5.3 Cardinalidade das Relações

| Relação | Tipo | Descrição |
|---------|------|-----------|
| User → TeamMember | 1:N | Um user pode estar em várias equipas |
| Event → Team | 1:N | Um evento pode ter várias equipas |
| Team → TeamMember | 1:N | Uma equipa pode ter vários membros |
| Event → Challenge | 1:N | Um evento pode ter vários desafios |
| Event → Project | 1:N | Um evento pode ter vários projetos |
| Team → Project | 1:N | Uma equipa pode ter um projeto (por evento) |
| Project → Evaluation | 1:N | Um projeto pode ter várias avaliações |
| User → Evaluation | 1:N | Um jurado pode fazer várias avaliações |
| User → Notification | 1:N | Um user pode ter várias notificações |
| User → Certificate | 1:N | Um user pode ter vários certificados |

---

## 6. API (Design Conceitual)

### 6.1 Convenções da API

**Base URL:** `http://localhost:8000/api/v1`

**Headers padrão:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Formato de resposta padrão (sucesso):**
```json
{
  "id": "uuid",
  "name": "Hackathon XYZ",
  "description": "Descrição...",
  "created_at": "2026-06-18T12:00:00Z"
}
```

**Formato de resposta padrão (erro):**
```json
{
  "detail": "Mensagem de erro",
  "status_code": 400
}
```

**Formato de paginação:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```

### 6.2 Lista Completa de Endpoints

#### Autenticação (`/auth`)

```
POST   /auth/register           → Criar conta
POST   /auth/login              → Fazer login
POST   /auth/refresh            → Renovar token
POST   /auth/verify-email/{token} → Verificar email
POST   /auth/password-reset     → Pedir reset password
POST   /auth/password-reset/confirm → Confirmar reset
GET    /auth/me                 → Ver perfil próprio
PUT    /auth/me                 → Editar perfil próprio
```

#### Utilizadores (`/users`)

```
GET    /users                   → Listar utilizadores (admin)
GET    /users/{id}              → Ver perfil de outro user
GET    /users/{id}/certificates → Ver certificados do user
```

#### Eventos (`/events`)

```
GET    /events                  → Listar eventos
POST   /events                  → Criar evento
GET    /events/{id}             → Ver detalhes do evento
PUT    /events/{id}             → Editar evento
DELETE /events/{id}             → Apagar evento
PATCH  /events/{id}/status      → Mudar estado
```

#### Equipas (`/events/{event_id}/teams`)

```
GET    /events/{eid}/teams                  → Listar equipas
POST   /events/{eid}/teams                  → Criar equipa
GET    /events/{eid}/teams/{tid}            → Ver equipa
POST   /events/{eid}/teams/{tid}/invite     → Convidar
POST   /events/{eid}/teams/join             → Entrar por código
POST   /events/{eid}/teams/{tid}/accept/{uid} → Aceitar membro
POST   /events/{eid}/teams/{tid}/reject/{uid} → Rejeitar
DELETE /events/{eid}/teams/{tid}/leave      → Sair
DELETE /events/{eid}/teams/{tid}/members/{uid} → Remover
```

#### Desafios (`/events/{event_id}/challenges`)

```
GET    /events/{eid}/challenges             → Listar desafios
POST   /events/{eid}/challenges             → Criar desafio
GET    /events/{eid}/challenges/{cid}       → Ver desafio
PUT    /events/{eid}/challenges/{cid}       → Editar
DELETE /events/{eid}/challenges/{cid}       → Apagar
GET    /events/{eid}/challenges/categories  → Listar categorias
POST   /events/{eid}/challenges/categories  → Criar categoria
POST   /events/{eid}/challenges/criteria    → Criar critério
```

#### Projetos (`/events/{event_id}/projects`)

```
GET    /events/{eid}/projects               → Listar projetos
POST   /events/{eid}/projects               → Submeter projeto
GET    /events/{eid}/projects/{pid}         → Ver projeto
PUT    /events/{eid}/projects/{pid}         → Editar
POST   /events/{eid}/projects/{pid}/submit  → Finalizar
```

#### Avaliações (`/events/{event_id}/evaluations`)

```
POST   /events/{eid}/evaluations            → Submeter avaliação
GET    /events/{eid}/evaluations/projects/{pid} → Avaliações do projeto
GET    /events/{eid}/evaluations/ranking    → Ver ranking
GET    /events/{eid}/evaluations/my         → Minhas avaliações
```

#### Ranking (`/events/{event_id}/ranking`)

```
GET    /events/{eid}/ranking                → Ranking completo
GET    /events/{eid}/ranking/stream         → SSE (tempo real)
```

#### Certificados (`/certificates`)

```
GET    /certificates/verify/{code}          → Verificar certificado
GET    /certificates/download/{id}          → Download PDF
```

#### Notificações (`/notifications`)

```
GET    /notifications                       → Listar notificações
PUT    /notifications/{id}/read             → Marcar como lida
PUT    /notifications/read-all              → Marcar todas lidas
```

#### IA (`/ai`)

```
POST   /ai/events/{eid}/ask                 → Perguntar ao assistente
POST   /ai/evaluate/{project_id}            → Avaliação por IA
POST   /ai/events/{eid}/suggest-teams       → Sugerir equipas
```

#### Dashboard (`/dashboard`)

```
GET    /dashboard/stats                     → Estatísticas globais
GET    /dashboard/events/{eid}/stats        → Stats do evento
```

---

## 7. Estrutura Completa de Pastas

```
hackhub/
│
├── backend/                                 ← Backend FastAPI (Python)
│   ├── app/                                 ← Código principal da aplicação
│   │   ├── __init__.py                      ← Torna "app" um pacote Python
│   │   │
│   │   ├── api/                             ← Camada de API (Endpoints REST)
│   │   │   ├── __init__.py
│   │   │   └── v1/                          ← Versão 1 da API
│   │   │       ├── __init__.py
│   │   │       └── endpoints/               ← Rotas organizadas por domínio
│   │   │           ├── __init__.py
│   │   │           ├── auth.py              → /auth (login, register, refresh)
│   │   │           ├── events.py            → /events (CRUD eventos)
│   │   │           ├── teams.py             → /teams (gestão de equipas)
│   │   │           ├── challenges.py        → /challenges (desafios)
│   │   │           ├── projects.py          → /projects (submissões)
│   │   │           ├── evaluations.py       → /evaluations (avaliações)
│   │   │           ├── ranking.py           → /ranking (classificação)
│   │   │           ├── users.py             → /users (perfis)
│   │   │           ├── certificates.py      → /certificates
│   │   │           ├── notifications.py     → /notifications
│   │   │           ├── ai.py                → /ai (funcionalidades IA)
│   │   │           └── dashboard.py         → /dashboard (estatísticas)
│   │   │
│   │   ├── core/                            ← Configurações e infraestrutura
│   │   │   ├── __init__.py
│   │   │   ├── config.py                    → Configurações (variáveis de ambiente)
│   │   │   ├── database.py                  → Conexão PostgreSQL (async)
│   │   │   ├── security.py                  → JWT, bcrypt, hashing
│   │   │   └── deps.py                      → Dependências (get_current_user, etc.)
│   │   │
│   │   ├── models/                          ← Modelos SQLAlchemy (ORM)
│   │   │   ├── __init__.py
│   │   │   ├── user.py                      → User model
│   │   │   ├── event.py                     → Event model
│   │   │   ├── team.py                      → Team + TeamMember models
│   │   │   ├── challenge.py                 → Challenge + Category + Criterion
│   │   │   ├── project.py                   → Project model
│   │   │   ├── evaluation.py                → Evaluation + EvaluationScore
│   │   │   ├── certificate.py               → Certificate model
│   │   │   └── notification.py              → Notification model
│   │   │
│   │   ├── schemas/                         ← Esquemas Pydantic (DTOs)
│   │   │   ├── __init__.py
│   │   │   ├── user.py                      → UserCreate, UserResponse, TokenResponse
│   │   │   ├── event.py                     → EventCreate, EventResponse
│   │   │   ├── team.py                      → TeamCreate, TeamResponse
│   │   │   ├── challenge.py                 → ChallengeCreate, ChallengeResponse
│   │   │   ├── project.py                   → ProjectCreate, ProjectResponse
│   │   │   ├── evaluation.py                → EvaluationCreate, EvaluationResponse
│   │   │   ├── certificate.py               → CertificateResponse
│   │   │   └── notification.py              → NotificationResponse
│   │   │
│   │   ├── services/                        ← Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py              → Registo, login, tokens
│   │   │   ├── user_service.py              → Perfis, estatísticas
│   │   │   ├── event_service.py             → CRUD eventos, transições
│   │   │   ├── team_service.py              → Equipas, convites
│   │   │   ├── project_service.py           → Submissões
│   │   │   ├── evaluation_service.py        → Avaliações, notas
│   │   │   ├── ranking_service.py           → Cálculo ranking, cache
│   │   │   ├── notification_service.py      → Notificações multicanal
│   │   │   ├── certificate_service.py       → PDF, QR Code
│   │   │   └── ai_service.py                → OpenAI, sugestões
│   │   │
│   │   ├── repositories/                    ← Acesso a dados (queries)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      → CRUD genérico (get, create, update)
│   │   │   ├── user_repository.py           → Queries de utilizadores
│   │   │   ├── event_repository.py          → Queries de eventos
│   │   │   ├── team_repository.py           → Queries de equipas
│   │   │   ├── project_repository.py        → Queries de projetos
│   │   │   ├── evaluation_repository.py     → Queries de avaliações
│   │   │   └── notification_repository.py   → Queries de notificações
│   │   │
│   │   └── utils/                           ← Utilitários
│   │       ├── __init__.py
│   │       ├── email.py                     → Envio de emails (SMTP)
│   │       └── helpers.py                   → Funções auxiliares
│   │
│   ├── alembic/                             ← Migrações de base de dados
│   │   ├── env.py                           → Configuração do Alembic
│   │   └── versions/                        → Ficheiros de migração
│   │
│   ├── tests/                               ← Testes automatizados
│   │   ├── __init__.py
│   │   ├── conftest.py                      → Fixtures (test client, DB test)
│   │   ├── test_auth.py                     → Testes de autenticação
│   │   └── test_events.py                   → Testes de eventos
│   │
│   ├── requirements.txt                     ← Dependências Python
│   ├── Dockerfile                           → Docker para o backend
│   └── .env.example                         → Exemplo de variáveis de ambiente
│
├── frontend/                                ← Frontend Next.js (TypeScript)
│   ├── src/                                 ← Código fonte
│   │   ├── app/                             ← App Router (páginas + layouts)
│   │   │   ├── layout.tsx                   → Layout raiz (Navbar, Footer, Providers)
│   │   │   ├── page.tsx                     → Landing page (página inicial)
│   │   │   ├── loading.tsx                  → Loading state global
│   │   │   ├── error.tsx                    → Error boundary global
│   │   │   ├── not-found.tsx                → Página 404
│   │   │   │
│   │   │   ├── auth/                        → Páginas de autenticação
│   │   │   │   ├── login/page.tsx           → Login
│   │   │   │   ├── register/page.tsx        → Registo
│   │   │   │   ├── forgot-password/page.tsx → Recuperar password
│   │   │   │   └── reset-password/page.tsx  → Reset password
│   │   │   │
│   │   │   ├── events/                      → Páginas de eventos
│   │   │   │   ├── page.tsx                 → Lista de eventos
│   │   │   │   └── [id]/                    → Página de detalhe dinâmica
│   │   │   │       ├── page.tsx             → Detalhes do evento
│   │   │   │       └── register/page.tsx    → Inscrição no evento
│   │   │   │
│   │   │   ├── teams/                       → Páginas de equipas
│   │   │   │   ├── page.tsx                 → Minhas equipas
│   │   │   │   └── [id]/page.tsx            → Detalhes da equipa
│   │   │   │
│   │   │   ├── profile/page.tsx             → Perfil do utilizador
│   │   │   │
│   │   │   └── dashboard/                   → Páginas de dashboard
│   │   │       ├── page.tsx                 → Dashboard principal
│   │   │       └── events/                  → Gestão de eventos
│   │   │           ├── page.tsx             → Lista de eventos (organizador)
│   │   │           └── [id]/page.tsx        → Gestão de evento específico
│   │   │
│   │   ├── components/                      ← Componentes React
│   │   │   ├── ui/                          → Componentes base (shadcn/ui)
│   │   │   │   ├── button.tsx               → Botão com variantes
│   │   │   │   ├── input.tsx                → Input com label e erro
│   │   │   │   ├── card.tsx                 → Card + Header + Content + Footer
│   │   │   │   ├── badge.tsx                → Badge com cores
│   │   │   │   ├── avatar.tsx               → Avatar com fallback
│   │   │   │   ├── skeleton.tsx             → Loading skeleton
│   │   │   │   ├── dialog.tsx               → Modal
│   │   │   │   ├── tabs.tsx                 → Tabs
│   │   │   │   ├── select.tsx               → Select dropdown
│   │   │   │   ├── toast.tsx                → Toast notifications
│   │   │   │   ├── progress.tsx             → Progress bar
│   │   │   │   ├── switch.tsx               → Toggle switch
│   │   │   │   ├── separator.tsx            → Separador visual
│   │   │   │   ├── tooltip.tsx              → Tooltip
│   │   │   │   ├── accordion.tsx            → Accordion (FAQ)
│   │   │   │   ├── scroll-area.tsx          → Scroll customizado
│   │   │   │   ├── data-table.tsx           → Tabela com paginação
│   │   │   │   ├── empty-state.tsx          → Estado vazio
│   │   │   │   ├── loading-state.tsx        → Estado de loading
│   │   │   │   ├── error-state.tsx          → Estado de erro
│   │   │   │   └── dropdown-menu.tsx        → Dropdown menu
│   │   │   │
│   │   │   ├── layout/                      → Componentes de layout
│   │   │   │   ├── navbar.tsx               → Barra de navegação
│   │   │   │   ├── footer.tsx               → Rodapé
│   │   │   │   ├── sidebar.tsx              → Sidebar do dashboard
│   │   │   │   ├── theme-toggle.tsx         → Alternar tema
│   │   │   │   └── providers.tsx            → Providers (QueryClient, Theme)
│   │   │   │
│   │   │   ├── shared/                      → Componentes partilhados
│   │   │   │   ├── event-card.tsx           → Card de evento
│   │   │   │   ├── team-card.tsx            → Card de equipa
│   │   │   │   ├── project-card.tsx         → Card de projeto
│   │   │   │   ├── ranking-table.tsx        → Tabela de classificação
│   │   │   │   └── notification-bell.tsx    → Sino de notificações
│   │   │   │
│   │   │   └── forms/                       → Formulários
│   │   │       ├── login-form.tsx           → Formulário de login
│   │   │       ├── register-form.tsx        → Formulário de registo
│   │   │       ├── event-form.tsx           → Formulário de evento
│   │   │       ├── team-form.tsx            → Formulário de equipa
│   │   │       └── project-form.tsx         → Formulário de projeto
│   │   │
│   │   ├── hooks/                           ← Custom hooks (TanStack Query)
│   │   │   ├── useAuth.ts                   → Hook de autenticação
│   │   │   ├── useEvents.ts                 → Hook de eventos
│   │   │   ├── useTeams.ts                  → Hook de equipas
│   │   │   ├── useProjects.ts              → Hook de projetos
│   │   │   ├── useRanking.ts               → Hook de ranking
│   │   │   ├── useNotifications.ts         → Hook de notificações
│   │   │   └── useDashboard.ts             → Hook de dashboard
│   │   │
│   │   ├── lib/                             → Bibliotecas e utilitários
│   │   │   ├── api.ts                       → Axios client com interceptors
│   │   │   └── utils.ts                     → Funções auxiliares (cn, formatDate)
│   │   │
│   │   ├── store/                           → Estado global (Zustand)
│   │   │   ├── auth.store.ts                → Store de autenticação
│   │   │   └── theme.store.ts               → Store de tema
│   │   │
│   │   └── types/                           → Tipos TypeScript
│   │       └── index.ts                    → Interfaces e tipos
│   │
│   ├── styles/
│   │   └── globals.css                      → CSS global + variáveis de tema
│   │
│   ├── public/                              → Ficheiros estáticos
│   ├── package.json                         → Dependências Node.js
│   ├── tsconfig.json                        → Configuração TypeScript
│   ├── tailwind.config.ts                   → Configuração Tailwind
│   ├── next.config.js                       → Configuração Next.js
│   ├── postcss.config.js                    → Configuração PostCSS
│   ├── Dockerfile                           → Docker para frontend
│   └── .env.example                         → Exemplo de env vars
│
├── nginx/                                   ← Configuração Nginx
│   └── nginx.conf                           → Reverse proxy + CORS + cache
│
├── .github/                                 ← GitHub
│   └── workflows/
│       └── ci.yml                           → CI/CD Pipeline
│
├── scripts/                                 ← Scripts auxiliares
│   ├── setup.ps1                            → Setup em PowerShell
│   └── dev.bat                              → Iniciar dev com Docker
│
├── docs/                                    ← Documentação
│   └── REPORT.md                            ← Este relatório técnico
│
├── assets/                                  → Recursos estáticos (logo, etc.)
├── docker-compose.yml                       → Orquestração Docker
├── .gitignore                               → Ficheiros ignorados pelo Git
├── LICENSE                                   → Licença MIT
└── README.md                                → Documentação principal
```

### 7.1 Responsabilidade de cada pasta principal

| Pasta | Responsabilidade |
|-------|-----------------|
| `backend/` | Todo o código do servidor, API, lógica de negócio e dados |
| `backend/app/` | Pacote principal da aplicação FastAPI |
| `backend/app/api/` | Endpoints REST — a "porta de entrada" do backend |
| `backend/app/core/` | Infraestrutura: config, DB, segurança, dependências |
| `backend/app/models/` | Definição das tabelas da base de dados (ORM) |
| `backend/app/schemas/` | DTOs para validação de input/output |
| `backend/app/services/` | Regras de negócio — o "cérebro" da aplicação |
| `backend/app/repositories/` | Consultas SQL — acesso a dados |
| `backend/app/utils/` | Utilitários: email, helpers |
| `backend/alembic/` | Migrações automáticas da base de dados |
| `backend/tests/` | Testes unitários e de integração |
| `frontend/` | Todo o código do frontend |
| `frontend/src/app/` | Páginas e layouts (App Router) |
| `frontend/src/components/` | Componentes React reutilizáveis |
| `frontend/src/hooks/` | Custom hooks com TanStack Query |
| `frontend/src/lib/` | API client e utilitários |
| `frontend/src/store/` | Estado global com Zustand |
| `frontend/src/types/` | Tipos TypeScript |
| `nginx/` | Configuração do proxy reverso |
| `scripts/` | Scripts de setup e desenvolvimento |
| `docs/` | Documentação do projeto |

---

## 8. Explicação de Cada Ficheiro

### 8.1 Ficheiros Raiz

#### `docker-compose.yml`
**O que faz:** Orquestra todos os serviços (PostgreSQL, Redis, Backend, Frontend, Nginx).
**Porque existe:** Permite que toda a stack funcione com um único comando: `docker compose up`.
**Como interage:** Define dependências entre serviços (backend depende de postgres e redis).

#### `.gitignore`
**O que faz:** Lista ficheiros que não devem ser versionados (env, node_modules, __pycache__).
**Porque existe:** Evita que ficheiros sensíveis ou desnecessários sejam enviados para o GitHub.

#### `LICENSE`
**O que faz:** Licença MIT do projeto.
**Porque existe:** Define os termos legais de uso e distribuição do código.

#### `README.md`
**O que faz:** Documentação principal do projeto.
**Porque existe:** Apresenta o projeto, instruções de setup, links úteis.

### 8.2 Backend — Core

#### `backend/app/__init__.py`
**O que faz:** Torna a pasta `app` um pacote Python importável.
**Porque existe:** Necessário para o Python reconhecer a pasta como módulo.

#### `backend/app/core/config.py`
**O que faz:** Carrega todas as variáveis de ambiente e disponibiliza como objeto `settings`.
**Porque existe:** Centraliza toda a configuração da aplicação.
**Exemplo de uso:** `settings.DATABASE_URL`, `settings.SECRET_KEY`
**Padrão usado:** Pydantic BaseSettings (validação automática das env vars).

#### `backend/app/core/database.py`
**O que faz:** Cria a conexão assíncrona com PostgreSQL usando SQLAlchemy.
**Porque existe:** Fornece a sessão de base de dados para toda a aplicação.
**Componentes:**
- `engine` — Conexão principal
- `async_session_factory` — Fábrica de sessões
- `Base` — Classe base para todos os modelos ORM
- `get_db()` — Generator que fornece uma sessão por request

#### `backend/app/core/security.py`
**O que faz:** Implementa hashing de passwords (bcrypt) e criação/validação de JWT.
**Porque existe:** Segurança da autenticação.
**Funções:**
- `verify_password(plain, hashed)` — Verifica password
- `get_password_hash(password)` — Gera hash
- `create_access_token(data)` — Cria JWT de curta duração
- `create_refresh_token(data)` — Cria JWT de longa duração
- `decode_token(token)` — Valida e decodifica JWT

#### `backend/app/core/deps.py`
**O que faz:** Define dependências injetáveis nos endpoints.
**Porque existe:** Reutilização de lógica de autenticação e autorização.
**Dependências:**
- `get_current_user` — Extrai user do token JWT
- `get_current_active_user` — Verifica se user está ativo
- `get_current_admin` — Verifica role ADMIN
- `get_current_organizer` — Verifica role ADMIN ou ORGANIZER

### 8.3 Backend — Models

#### `backend/app/models/user.py`
**O que faz:** Define a tabela `users` e as relações com outras tabelas.
**Porque existe:** Representa os utilizadores na base de dados.
**Padrão usado:** SQLAlchemy 2.0 com `Mapped` e `mapped_column` (type-safe).

#### `backend/app/models/event.py`
**O que faz:** Define a tabela `events` com todos os campos do evento.
**Porque existe:** Armazena dados dos hackathons.

#### `backend/app/models/team.py`
**O que faz:** Define `teams` e `team_members`.
**Porque existe:** Equipas e membros são entidades separadas (N para N).

#### `backend/app/models/challenge.py`
**O que faz:** Define `challenges`, `challenge_categories` e `criteria`.
**Porque existe:** Desafios, categorias e critérios são hierárquicos.

#### `backend/app/models/project.py`
**O que faz:** Define `projects` e `project_technologies`.
**Porque existe:** Projetos submetidos por equipas.

#### `backend/app/models/evaluation.py`
**O que faz:** Define `evaluations` e `evaluation_scores`.
**Porque existe:** Avaliações com pontuações por critério.

#### `backend/app/models/certificate.py`
**O que faz:** Define `certificates`.
**Porque existe:** Certificados gerados automaticamente.

#### `backend/app/models/notification.py`
**O que faz:** Define `notifications`.
**Porque existe:** Notificações para utilizadores.

### 8.4 Backend — Schemas (Pydantic)

**O que faz cada schema:** Define a estrutura dos dados que entram (requests) e saem (responses) da API.

| Schema | Request | Response |
|--------|---------|----------|
| `UserCreate` | email, username, password, full_name | — |
| `UserResponse` | — | Todos os campos do user |
| `TokenResponse` | — | access_token, refresh_token, token_type |
| `EventCreate` | title, description, start_date, etc. | — |
| `EventResponse` | — | Todos os campos do evento |
| `TeamCreate` | name, description | — |
| `TeamResponse` | — | Equipa + membros |
| `ProjectCreate` | name, description, github_url, etc. | — |
| `ProjectResponse` | — | Projeto completo |

**Porque usar DTOs (Data Transfer Objects)?**
1. **Segurança** — Controlamos exatamente o que o cliente pode enviar
2. **Validação** — Pydantic valida tipos, formatos, obrigatoriedade
3. **Documentação** — Geram automaticamente o schema do Swagger
4. **Separação** — A entidade (model) não é exposta diretamente

### 8.5 Backend — Services

#### `auth_service.py`
**O que faz:** Registo, login, refresh tokens, verificação email, reset password.
**Funções principais:**
- `register()` — Valida unique, hasheia password, cria user, envia email
- `login()` — Verifica credenciais, gera tokens
- `refresh_token()` — Valida refresh, emite novo access
- `verify_email()` — Decodifica token, marca verified
- `send_password_reset()` — Gera token, envia email
- `confirm_password_reset()` — Valida token, atualiza password

#### `event_service.py`
**O que faz:** CRUD de eventos com máquina de estados.
**Regras:**
- Só organizer/admin cria
- Transições de status válidas (draft→published→in_progress→closed)

#### `team_service.py`
**O que faz:** Gestão completa de equipas.
**Funcionalidades:**
- Criar equipa com código único
- Convidar membros (gera código)
- Aceitar/rejeitar convites
- Validar tamanho da equipa (min/max do evento)

#### `project_service.py`
**O que faz:** Submissão e edição de projetos.
**Regras:**
- Múltiplas atualizações até fecho
- Status: draft → submitted → finalized

#### `evaluation_service.py`
**O que faz:** Submeter avaliações e calcular notas.
**Cálculo:** `nota_final = Σ(score × peso) / Σ(pesos)`

#### `ranking_service.py`
**O que faz:** Calcular ranking e manter cache em Redis.
**Funcionalidades:**
- Ranking ordenado por nota total
- SSE para atualizações em tempo real
- Cache em Redis para performance

#### `certificate_service.py`
**O que faz:** Gerar PDFs com QR Code e assinatura digital.
**Ferramentas:** WeasyPrint (PDF), qrcode (QR Code)

#### `notification_service.py`
**O que faz:** Enviar notificações (email, Telegram).
**Funcionalidades:**
- Template de email
- Mensagem Telegram
- Guardar histórico na DB

#### `ai_service.py`
**O que faz:** Integração com OpenAI.
**Funcionalidades:**
- Assistente do evento (baseado no FAQ)
- Avaliação assistida (análise de projeto)
- Sugestão de equipas (matching algorithm)

### 8.6 Backend — Endpoints

Cada ficheiro de endpoint segue o mesmo padrão:

```python
# 1. Importações
# 2. Criação do router
router = APIRouter(prefix="/events", tags=["Events"])

# 3. Dependências (auth, db)
# 4. Endpoints com docstrings e type hints
@router.get("/", response_model=PaginatedResponse[EventResponse])
async def list_events(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """Lista todos os eventos com paginação."""
    service = EventService(db)
    return await service.list_events(page=page, size=size)
```

**Padrão:**
1. Router define o prefixo e tags
2. Endpoints têm type hints para request/response
3. Dependências são injetadas via `Depends()`
4. Service é instanciado com a sessão DB
5. Service executa a lógica de negócio
6. Response é automaticamente validada pelo schema Pydantic

### 8.7 Frontend — API Client

#### `frontend/src/lib/api.ts`
**O que faz:** Cliente Axios configurado com interceptors.
**Características:**
- Base URL do `NEXT_PUBLIC_API_URL`
- Interceptor de request: adiciona Bearer token
- Interceptor de response: refresh automático em 401
- Queue de requests falhados durante refresh
- Funções tipadas para cada endpoint da API

**Fluxo do interceptor de 401:**
```
1. Request falha com 401 (token expirado)
2. Interceptor captura o erro
3. Verifica se há refresh token
4. Tenta renovar token
5. Se sucesso: retry request original
6. Se falha: redireciona para login
```

### 8.8 Frontend — Hooks (TanStack Query)

Cada hook encapsula queries e mutations para um domínio:

```typescript
// useEvents.ts
export function useEvents(filters: EventFilters) {
  return useQuery({
    queryKey: ['events', filters],
    queryFn: () => apiClient.events.list(filters),
  })
}

export function useCreateEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateEventRequest) => apiClient.events.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      toast.success('Evento criado com sucesso!')
    },
  })
}
```

**Porque TanStack Query?**
- Cache automático de dados
- Refetch em background
- Paginação e infinite scroll
- Mutations com invalidação de cache
- Loading/error states automáticos
- Polling para dados em tempo real

### 8.9 Frontend — Store (Zustand)

#### `auth.store.ts`
**O que faz:** Gerencia o estado de autenticação.
**Estado:**
- `user: User | null` — Dados do utilizador
- `tokens: AuthTokens | null` — Access + Refresh tokens
- `isAuthenticated: boolean` — Está autenticado?
- `isLoading: boolean` — A carregar?

**Ações:**
- `login()` — Chama API, guarda tokens no localStorage
- `register()` — Chama API de registo
- `logout()` — Limpa tokens, redireciona
- `refreshToken()` — Renova access token
- `loadFromStorage()` — Recupera sessão ao iniciar

#### `theme.store.ts`
**O que faz:** Gerencia o tema (light/dark/system).
**Integração:** next-themes para aplicar a classe `dark` no HTML.

---

## 9. Regras de Engenharia

### 9.1 Princípios SOLID Aplicados

| Princípio | Como aplicamos no HackHub |
|-----------|---------------------------|
| **S** — Single Responsibility | Cada service tem uma responsabilidade única (AuthService só trata de auth) |
| **O** — Open/Closed | Repositórios estendem BaseRepository, services são injetados |
| **L** — Liskov Substitution | Qualquer repositório pode substituir o BaseRepository |
| **I** — Interface Segregation | Schemas Pydantic são específicos para cada operação |
| **D** — Dependency Inversion | Endpoints dependem de Services (abstrações), não de implementações concretas |

### 9.2 Clean Architecture

Aplicamos Clean Architecture com 3 camadas principais:

```
Camada 1: Endpoints (API)     → Só trata HTTP
Camada 2: Services (Negócio)  → Lógica da aplicação
Camada 3: Repositories (Dados) → Acesso a dados
```

**Regras de dependência:**
- Endpoints → Services (✅ permitido)
- Services → Repositories (✅ permitido)
- Endpoints → Repositories (❌ proibido)
- Services → Endpoints (❌ proibido)

### 9.3 DRY (Don't Repeat Yourself)

- `BaseRepository` com CRUD genérico evita repetir queries
- `core/deps.py` com dependências reutilizáveis
- Componentes shadcn/ui reutilizáveis em todo o frontend
- Hooks TanStack Query encapsulam lógica de data fetching

### 9.4 KISS (Keep It Simple, Stupid)

- Endpoints pequenos e focados (máx 10-15 linhas)
- Services com métodos coesos (uma função, uma responsabilidade)
- Componentes React divididos por função (ui, layout, shared, forms)
- Evitar over-engineering: preferimos código claro a código "inteligente"

### 9.5 Segurança

| Prática | Implementação |
|---------|--------------|
| **Password Hashing** | bcrypt via passlib |
| **JWT Seguro** | Access token 15min + Refresh token 7dias |
| **CORS** | Apenas origens configuradas |
| **Rate Limiting** | slowapi (5 tentativas/min para login) |
| **Input Validation** | Pydantic schemas validam tudo |
| **SQL Injection** | SQLAlchemy ORM (queries parametrizadas) |
| **XSS** | Sanitização de inputs + CSP headers |
| **RBAC** | Roles: admin, organizer, judge, participant |
| **Audit Logging** | Logs de operações sensíveis |

### 9.6 Escalabilidade

**Estratégias de escalabilidade no HackHub:**

1. **Async I/O** — FastAPI + asyncpg permitem milhares de conexões simultâneas
2. **Caching** — Redis para ranking, sessões, dados frequentes
3. **Paginação** — Todos os endpoints de listagem são paginados
4. **Índices DB** — Campos de pesquisa (email, username, status) têm índices
5. **Horizontal Scaling** — Backend stateless, pode ser replicado
6. **Connection Pooling** — SQLAlchemy com pool de conexões
7. **SSE vs WebSocket** — SSE é mais leve para ranking (unidirecional)

### 9.7 Tratamento de Erros

**Backend:** Exception handlers globais no `main.py`:
```python
@app.exception_handler(HTTPException)    → Erros HTTP (400, 401, 404, etc.)
@app.exception_handler(ValidationError)  → Erros de validação Pydantic (422)
@app.exception_handler(Exception)        → Erros genéricos (500)
```

**Frontend:** Error boundaries + TanStack Query error states:
```
Páginas:     error.tsx (error boundary global)
Componentes: ErrorState (erro com retry)
Mutations:   toast.error() (erros de formulário)
Queries:     isError → mostrar ErrorState
```

### 9.8 Testes

**Estratégia de testes:**

| Tipo | O que testar | Ferramenta |
|------|-------------|-----------|
| Unitários | Services com DB mock | pytest + pytest-asyncio |
| Integração | Endpoints completos | TestClient (FastAPI) |
| Frontend | Componentes (futuro) | Vitest + Testing Library |

**Boas práticas de teste:**
- Testes isolados (cada teste cria e limpa os seus dados)
- Fixtures para dados comuns (user test, event test)
- Nomenclatura: `test_<funcao>_<cenario>`
- Cobertura mínima: 80%

---

## 10. Comentários no Código

### 10.1 Exemplo Backend: Service de Autenticação

```python
# =============================================================================
# Serviço de Autenticação
# =============================================================================
# Responsabilidade: Gerir registo, login, refresh de tokens, verificação de
# email e recuperação de password.
#
# Padrão: Service Layer
#   - Recebe dados validados (do endpoint)
#   - Implementa regras de negócio
#   - Chama repositories para acesso a dados
#   - Retorna DTOs (Pydantic schemas)
# =============================================================================

class AuthService:
    """
    Serviço responsável por toda a lógica de autenticação.

    Métodos principais:
        - register: Cria nova conta de utilizador
        - login: Autentica e devolve tokens JWT
        - refresh_token: Renova access token expirado
        - verify_email: Confirma verificação de email
        - send_password_reset: Envia email com link de recuperação
        - confirm_password_reset: Atualiza password após reset
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa o serviço com uma sessão de base de dados.

        Args:
            db: Sessão assíncrona do SQLAlchemy (injetada pelo FastAPI)
        """
        self.db = db
        # Repositório especializado para operações de utilizador
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> User:
        """
        Regista um novo utilizador na plataforma.

        Fluxo:
            1. Verifica se email já existe → erro se duplicado
            2. Verifica se username já existe → erro se duplicado
            3. Hash da password com bcrypt (nunca guardar passwords em texto!)
            4. Cria o utilizador na base de dados
            5. Envia email de verificação
            6. Retorna o utilizador criado

        Args:
            user_data: Dados validados do formulário de registo

        Returns:
            User: Utilizador criado (sem a password!)

        Raises:
            HTTPException 400: Se email ou username já existirem
        """
        # Verificar unicidade do email
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email já está registado"
            )

        # Verificar unicidade do username
        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este username já está em uso"
            )

        # Hash seguro da password (bcrypt)
        hashed_password = get_password_hash(user_data.password)

        # Criar utilizador na base de dados
        user = await self.user_repo.create(User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.PARTICIPANT,  # Sempre PARTICIPANT por defeito
            is_active=True,
            is_verified=False,  # Precisa verificar email depois
        ))

        # Enviar email de verificação (assíncrono, não bloqueia o registo)
        await self._send_verification_email(user)

        return user
```

### 10.2 Exemplo Frontend: Auth Store (Zustand)

```typescript
// =============================================================================
// Store de Autenticação (Zustand)
// =============================================================================
// Responsabilidade: Gerir o estado global de autenticação no frontend.
//
// Porquê Zustand em vez de Context API?
//   - Menos boilerplate que Context + Reducer
//   - Performance (não causa re-renders em toda a árvore)
//   - Persistência simples (localStorage)
//   - TypeScript-friendly
// =============================================================================

interface AuthState {
  /** Dados do utilizador autenticado (null se não autenticado) */
  user: User | null
  /** Tokens JWT (access + refresh) guardados no localStorage */
  tokens: AuthTokens | null
  /** True enquanto verifica se há sessão ativa ao carregar */
  isLoading: boolean
  /** True se o utilizador está autenticado */
  isAuthenticated: boolean

  // Ações disponíveis
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<User>
  logout: () => void
  refreshToken: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  setUser: (user: User) => void
  loadFromStorage: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // Estado inicial: sem user, sem tokens, a carregar
  user: null,
  tokens: null,
  isLoading: true,
  isAuthenticated: false,

  /**
   * Autentica o utilizador com email e password.
   *
   * Fluxo:
   *   1. Chama API de login
   *   2. Guarda tokens no localStorage (persistência)
   *   3. Atualiza estado com tokens
   *   4. Busca dados do utilizador com o token
   */
  login: async (data: LoginRequest) => {
    const tokens = await apiClient.auth.login(data)

    // Persistir tokens para manter sessão entre refreshes
    localStorage.setItem('auth_tokens', JSON.stringify(tokens))
    set({ tokens, isAuthenticated: true })

    // Buscar dados completos do utilizador
    const user = await apiClient.auth.getMe()
    set({ user })
  },

  /**
   * Remove a autenticação (logout).
   *
   * Limpa tokens do localStorage e do estado.
   * O interceptor do Axios detectará a ausência de tokens
   * e redirecionará para o login.
   */
  logout: () => {
    localStorage.removeItem('auth_tokens')
    set({ user: null, tokens: null, isAuthenticated: false })
  },

  /**
   * Recupera sessão ao iniciar a aplicação.
   *
   * Este método é chamado no Provider (layout.tsx) assim que
   * a aplicação carrega. Verifica se há tokens no localStorage
   * e tenta renovar a sessão.
   */
  loadFromStorage: async () => {
    try {
      // Server-Side Rendering: não temos acesso ao localStorage
      if (typeof window === 'undefined') {
        set({ isLoading: false })
        return
      }

      // Verificar se há tokens guardados
      const tokensRaw = localStorage.getItem('auth_tokens')
      if (!tokensRaw) {
        set({ isLoading: false })
        return
      }

      // Restaurar sessão com tokens existentes
      const tokens: AuthTokens = JSON.parse(tokensRaw)
      set({ tokens, isAuthenticated: true })

      // Buscar dados do utilizador (se token expirou, o interceptor trata)
      const user = await apiClient.auth.getMe()
      set({ user, isLoading: false })
    } catch {
      // Se falhar (token inválido/expirado), limpar sessão
      localStorage.removeItem('auth_tokens')
      set({ user: null, tokens: null, isAuthenticated: false, isLoading: false })
    }
  },
}))
```

### 10.3 Exemplo Backend: Endpoint de Eventos

```python
# =============================================================================
# Router de Eventos
# =============================================================================
# Responsabilidade: Gerir operações CRUD de eventos.
#
# Cada endpoint segue o mesmo padrão:
#   1. Definir método HTTP e rota
#   2. Injetar dependências (db, user atual)
#   3. Instanciar service
#   4. Chamar service
#   5. Retornar resposta
#
# Segurança: Endpoints de escrita requerem role ORGANIZER ou ADMIN
# =============================================================================

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=PaginatedResponse[EventResponse])
async def list_events(
    # Dependências injetadas automaticamente pelo FastAPI
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    search: Optional[str] = Query(None, description="Pesquisar por nome"),
    current_user: User = Depends(get_current_user_optional),  # Auth opcional
):
    """
    Lista eventos com filtros e paginação.

    - Sem autenticação: vê apenas eventos publicados
    - Com autenticação: vê eventos do seu role
    - Organizador: vê os seus drafts
    """
    service = EventService(db)
    return await service.list_events(
        page=page,
        size=size,
        status=status,
        search=search,
        user=current_user,  # Para filtrar por role
    )
```

### 10.4 Exemplo Frontend: Hook de Eventos (TanStack Query)

```typescript
// =============================================================================
// Hook: useEvents
// =============================================================================
// Responsabilidade: Fornecer dados de eventos com cache automática.
//
// TanStack Query (React Query) gere:
//   - Cache dos dados (evita requests desnecessários)
//   - Refetch em background (dados sempre frescos)
//   - Estados: loading, error, success
//   - Paginação
//   - Mutations com invalidação automática de cache
// =============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

/**
 * Hook para listar eventos com filtros.
 *
 * @param filters - Filtros opcionais (status, search, page, size)
 * @returns Query result com dados, loading, error
 *
 * Exemplo de uso:
 *   const { data, isLoading, error } = useEvents({ status: 'published' })
 */
export function useEvents(filters?: EventFilters) {
  return useQuery({
    // queryKey identifica unicamente esta query no cache
    // Quando filters muda, uma nova query é criada
    queryKey: ['events', filters],

    // Função que busca os dados (só executada se necessário)
    queryFn: () => apiClient.events.list(filters || {}),

    // Manter dados anteriores enquanto novos carregam
    // Evita flash de loading ao mudar de página
    placeholderData: keepPreviousData,

    // Refetch automático a cada 30 segundos
    // Útil para eventos com estado a mudar frequentemente
    refetchInterval: 30000,
  })
}

/**
 * Hook para criar um novo evento (mutação).
 *
 * Após criar, invalida a cache de eventos para forçar refetch.
 * Mostra toast de sucesso/erro.
 */
export function useCreateEvent() {
  const queryClient = useQueryClient()

  return useMutation({
    // Função que executa a mutação
    mutationFn: (data: CreateEventRequest) => apiClient.events.create(data),

    // Callback executado em caso de sucesso
    onSuccess: () => {
      // Invalidar cache de eventos → força refetch da lista
      queryClient.invalidateQueries({ queryKey: ['events'] })
      toast.success('Evento criado com sucesso!')
    },

    // Callback em caso de erro
    onError: (error: Error) => {
      toast.error(error.message || 'Erro ao criar evento')
    },
  })
}
```

---

## Conclusão

Este relatório documenta a arquitetura completa do **HackHub**, uma plataforma open-source para gestão de hackathons.

### Resumo das Decisões Técnicas

| Decisão | Porquê |
|---------|--------|
| **FastAPI** | Performance async, validação automática, Swagger integrado |
| **Clean Architecture** | Separação clara de responsabilidades, testabilidade |
| **Next.js 14 App Router** | SSR, SSG, routing baseado em ficheiros, performance |
| **TanStack Query** | Cache automático, mutations, polling |
| **Zustand** | Estado global leve, sem boilerplate |
| **JWT** | Autenticação stateless, escalável |
| **PostgreSQL** | Robustez, JSONB para dados flexíveis, índices avançados |
| **Redis** | Cache de alta performance, pub/sub para tempo real |
| **Docker** | Ambiente consistente, deploy simplificado |
| **SSE vs WebSocket** | SSE mais leve para ranking (unidirecional) |

### Próximos Passos para a Equipa

1. **Setup local** — Seguir instruções no README.md
2. **Explorar o código** — Começar pelos `core/`, depois `models/`, `services/`, `endpoints/`
3. **Migrações DB** — Criar primeira migração com `alembic revision --autogenerate`
4. **Testar** — Executar testes com `pytest tests/ -v`
5. **Desenvolver** — Cada membro foca num módulo específico

---

*Documento gerado pela equipa de arquitetura do HackHub — Junho 2026*
