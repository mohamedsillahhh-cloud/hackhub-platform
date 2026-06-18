<div align="center">
  <img src="https://raw.githubusercontent.com/mohamedsillahhh-cloud/hackhub-platform/main/assets/logo.svg" alt="HackHub Logo" width="120" height="120" />
  <h1>HackHub</h1>
  <p><strong>The ultimate open-source platform for hackathons, competitions, and innovation events.</strong></p>

  <p>
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#api-docs">API Docs</a> •
    <a href="#contributing">Contributing</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome" />
    <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python 3.12" />
    <img src="https://img.shields.io/badge/node-20-green" alt="Node 20" />
    <img src="https://img.shields.io/badge/next.js-14-black" alt="Next.js 14" />
  </p>
</div>

---

## Overview

HackHub is a modern, production-ready platform designed to manage hackathons, coding competitions, innovation fairs, and university tech events. Built with scalability in mind, it serves thousands of concurrent users with real-time updates, AI-powered features, and an intuitive interface inspired by Linear, Notion, and Stripe.

### Why HackHub?

- **Open Source** — Fully transparent, community-driven, and free to use
- **Enterprise-Grade** — Clean architecture, SOLID principles, and security best practices
- **AI-Powered** — Smart team formation, project evaluation, and event assistant
- **Real-Time** — Live rankings, notifications, and collaboration features
- **Scalable** — Async Python backend, optimized queries, Redis caching, and horizontal scaling ready

---

## Features

### Event Management
- Create and manage hackathons with custom timelines, challenges, and judging criteria
- Multiple event statuses: Draft → Published → In Progress → Closed
- Sponsors, prizes, FAQ, and regulation management

### Smart Team Formation
- AI-powered team suggestions based on skills, languages, and experience
- Invite system with unique codes
- Configurable min/max team sizes
- Team leader and member management

### Project Submission
- Multi-format submissions: GitHub repo, demo video, presentation PDF
- Multiple updates allowed until event closing
- Technology stack tagging

### Real-Time Ranking
- Live leaderboard updates during evaluation
- Weighted scoring by customizable criteria
- Automatic tie-breaking
- SSE (Server-Sent Events) for real-time streaming

### AI Assistant
- **Event Assistant** — Answer questions about rules, schedule, and prizes
- **Smart Evaluation** — Analyze projects and generate automatic feedback
- **Team Formation** — Create balanced teams automatically

### Certification System
- Automatic PDF generation with QR codes
- Digital signatures for authenticity
- Public verification system
- Multiple templates: Participation, Finalist, Winner, Judge, Organizer

### Analytics Dashboard
- Global stats: users, events, projects, participants
- Interactive charts and graphs
- Technology usage insights
- University and country participation metrics

### Notification System
- Multi-channel: Email, Telegram, Push
- Event-based: Team invites, registration approval, new challenges, results

---

## Tech Stack

### Frontend

| Technology | Purpose |
|-----------|---------|
| **Next.js 14** (App Router) | React framework with SSR and RSC |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Accessible, reusable components |
| **TanStack Query** | Server state management and caching |
| **Zustand** | Client state management |
| **Framer Motion** | Animations and transitions |
| **Recharts** | Interactive charts |
| **Next-Themes** | Dark/Light mode |

### Backend

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | High-performance async Python framework |
| **SQLAlchemy 2.0** | Async ORM with modern patterns |
| **Alembic** | Database migrations |
| **PostgreSQL** | Primary database |
| **Redis** | Caching and real-time pub/sub |
| **JWT** | Secure authentication |
| **Celery** | Background task processing |

### DevOps

| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-service orchestration |
| **Nginx** | Reverse proxy and load balancing |
| **GitHub Actions** | CI/CD pipeline |

---

## Project Structure

```
hackhub/
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/endpoints/    # Route handlers
│   │   ├── core/                # Config, security, database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic DTOs
│   │   ├── services/            # Business logic
│   │   ├── repositories/        # Data access layer
│   │   └── utils/               # Helpers and utilities
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   └── requirements.txt
├── frontend/                     # Next.js React frontend
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   ├── components/          # UI, layout, shared, forms
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # API client, utilities
│   │   ├── store/               # Zustand stores
│   │   └── types/               # TypeScript types
│   ├── public/                  # Static assets
│   └── styles/                  # Global CSS
├── nginx/                        # Nginx configuration
├── .github/workflows/           # CI/CD pipelines
├── scripts/                      # Setup and development scripts
├── docker-compose.yml            # Multi-service Docker setup
└── README.md
```

---

## Architecture

HackHub follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                    │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐  │
│  │  Pages  │ │Components│ │  Hooks │ │  API Client  │  │
│  └─────────┘ └──────────┘ └────────┘ └──────┬───────┘  │
├──────────────────────────────────────────────┼──────────┤
│                     Nginx Reverse Proxy        │         │
├──────────────────────────────────────────────┼──────────┤
│                  Backend (FastAPI)            │         │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │         │
│  │ Endpoints│ │ Services │ │ Repositories │ │         │
│  └──────────┘ └──────────┘ └──────┬───────┘ │         │
├────────────────────────────────────┼──────────┼──────────┤
│                         PostgreSQL │  Redis   │          │
└────────────────────────────────────┴──────────┘──────────┘
```

### Key Architectural Decisions

- **Repository Pattern**: Abstracts data access, makes testing easier
- **Service Layer**: All business logic lives here, endpoints are thin
- **DTO Pattern**: Pydantic schemas ensure type safety at API boundaries
- **Async Everywhere**: Python async/await for I/O-bound operations
- **JWT Auth**: Access + Refresh token pattern for secure sessions
- **RBAC**: Role-based access control (Admin, Organizer, Judge, Participant)

---

## Getting Started

### Prerequisites

- **Node.js** 20+
- **Python** 3.12+
- **Docker** and **Docker Compose**
- **PostgreSQL** 16+ (or use Docker)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/mohamedsillahhh-cloud/hackhub-platform.git
cd hackhub-platform

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker compose up --build
```

### Manual Development Setup

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (via Docker)
docker compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs** (Swagger): http://localhost:8000/docs
- **API Docs** (ReDoc): http://localhost:8000/redoc

### Environment Variables

#### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://hackhub:hackhub_secret@localhost:5432/hackhub` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | (change in production) |
| `ENVIRONMENT` | Runtime environment | `development` |
| `SMTP_SERVER` | SMTP server for emails | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USERNAME` | SMTP username | |
| `SMTP_PASSWORD` | SMTP password | |
| `SMTP_FROM_EMAIL` | Sender email address | `noreply@hackhub.com` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |
| `OPENAI_API_KEY` | OpenAI API key (for AI features) | |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | |
| `AI_RATE_LIMIT_ASK` | Rate limit for AI assistant | `20/minute` |
| `AI_RATE_LIMIT_EVALUATE` | Rate limit for AI evaluation | `5/minute` |
| `AI_RATE_LIMIT_SUGGEST` | Rate limit for team suggestions | `3/minute` |
| `AI_DAILY_TOKEN_LIMIT` | Max OpenAI tokens per user/day | `100000` |

#### Frontend (`frontend/.env.local`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

---

## API Documentation

The API is fully documented with Swagger/OpenAPI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Authentication** | | |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh access token (cookie‑based) |
| POST | `/api/v1/auth/logout` | Logout and clear cookies |
| GET | `/api/v1/auth/me` | Get current user |
| PUT | `/api/v1/auth/me` | Update profile |
| **Events** | | |
| GET | `/api/v1/events` | List events |
| POST | `/api/v1/events` | Create event |
| GET | `/api/v1/events/{id}` | Get event details |
| PUT | `/api/v1/events/{id}` | Update event |
| **Teams** | | |
| GET | `/api/v1/events/{id}/teams` | List teams |
| POST | `/api/v1/events/{id}/teams` | Create team |
| POST | `/api/v1/events/{id}/teams/join` | Join team by code |
| **Projects** | | |
| POST | `/api/v1/events/{id}/projects` | Submit project |
| PUT | `/api/v1/events/{id}/projects/{pid}` | Update project |
| **Ranking** | | |
| GET | `/api/v1/events/{id}/ranking` | Get ranking |
| GET | `/api/v1/events/{id}/ranking/stream` | Real-time ranking (SSE) |
| **AI** | | |
| POST | `/api/v1/ai/events/{id}/ask` | Ask event assistant |
| POST | `/api/v1/ai/evaluate/{id}` | AI project evaluation |
| POST | `/api/v1/ai/events/{id}/suggest-teams` | Suggest teams |

---

## Database Schema

```mermaid
erDiagram
    User ||--o{ TeamMember : has
    User ||--o{ Evaluation : makes
    User ||--o{ Notification : receives
    User ||--o{ Certificate : owns
    Event ||--o{ Team : contains
    Event ||--o{ Challenge : has
    Event ||--o{ Project : receives
    Event ||--o{ Certificate : issues
    Event ||--|| User : "organized by"
    Team ||--o{ TeamMember : has
    Team ||--o{ Project : submits
    Challenge ||--o{ ChallengeCategory : categorized
    ChallengeCategory ||--o{ Criterion : evaluated
    Project ||--o{ Evaluation : gets
    Evaluation ||--o{ EvaluationScore : has
```

---

## Security

HackHub implements industry-standard security practices:

- **JWT Authentication** with access/refresh token rotation
- **Password Hashing** using bcrypt
- **CORS** with strict origin validation
- **Rate Limiting** with slowapi
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM
- **XSS Protection** via input sanitization and Content Security Policy
- **RBAC** (Role-Based Access Control) for all operations
- **Audit Logging** for sensitive operations

---

## Testing

```bash
# Run backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend type checking
cd frontend
npx tsc --noEmit
```

---

## Contributing

Contributions are welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for a complete guide covering:

- Local development setup
- Commit conventions (Conventional Commits)
- Branching strategy
- PR checklist (tests, linting, migrations)
- Code style guidelines
- Architecture overview

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Developed with ❤️ by [Mohamed Sillah](https://github.com/mohamedsillahhh-cloud)
- Inspired by platforms like Linear, Notion, and Stripe
- Built with the best open-source tools from the Python and JavaScript ecosystems

---

<div align="center">
  <p></p>
  <p>
  <a href="https://github.com/mohamedsillahhh-cloud/hackhub-platform/issues">Report Bug</a> •
  <a href="https://github.com/mohamedsillahhh-cloud/hackhub-platform/discussions">Discussions</a> •
  <a href="https://github.com/mohamedsillahhh-cloud/hackhub-platform/releases">Releases</a>
  </p>
</div>
