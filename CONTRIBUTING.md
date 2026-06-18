# Contributing to HackHub

First off, thanks for taking the time to contribute! 🎉

HackHub is an open-source hackathon management platform built with Next.js 14, FastAPI, PostgreSQL, and Redis. Every contribution — whether it's a bug fix, new feature, documentation improvement, or typo fix — is appreciated.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
  - [Branching](#branching)
  - [Commit Convention](#commit-convention)
  - [Running Tests](#running-tests)
  - [Code Style & Linting](#code-style--linting)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Opening a Pull Request](#opening-a-pull-request)
- [Architecture & Design Decisions](#architecture--design-decisions)

---

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainer.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose (optional, but recommended)

### Local Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mohamedsillahhh-cloud/hackhub-platform.git
   cd hackhub-platform
   ```

2. **Backend setup:**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Frontend setup:**

   ```bash
   cd frontend
   npm install
   ```

4. **Database setup (via Docker):**

   ```bash
   docker compose up -d postgres redis
   ```

   Or use your own PostgreSQL 16 and Redis 7 instances.

5. **Run database migrations:**

   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Start the development servers:**

   ```bash
   # Terminal 1 — backend
   cd backend
   uvicorn app.main:app --reload --port 8000

   # Terminal 2 — frontend
   cd frontend
   npm run dev
   ```

   The API will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

### Environment Variables

Copy `.env.example` to `.env` in both `backend/` and `frontend/` and adjust:

**Backend** (`backend/.env`):

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hackhub
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-at-least-32-chars
OPENAI_API_KEY=sk-...  # Optional, for AI features
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

**Frontend** (`frontend/.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Project Structure

```
backend/app/
├── api/v1/endpoints/     → Route handlers (one file per domain)
├── core/                 → Config, security, DB session, dependencies
├── models/               → SQLAlchemy ORM models
├── schemas/              → Pydantic request/response DTOs
├── services/             → Business logic layer
├── repositories/         → Data access layer
└── utils/                → Email, helpers, etc.

frontend/src/
├── app/                  → Next.js App Router pages
├── components/           → Reusable UI components (shadcn/ui)
├── hooks/                → TanStack Query hooks
├── store/                → Zustand state management
├── lib/                  → API client, utilities
└── types/                → TypeScript type definitions
```

---

## Development Workflow

### Branching

- `main` — stable, release-ready
- `feat/<name>` — new features
- `fix/<name>` — bug fixes
- `docs/<name>` — documentation only

Always branch off `main` and open PRs targeting `main`.

### Commit Convention

We follow **Conventional Commits**:

```
<type>: <short description>

[optional body]
```

Types:

| Type       | Usage                                   |
|------------|----------------------------------------|
| `feat`     | A new feature                          |
| `fix`      | A bug fix                              |
| `refactor` | Code change that neither fixes nor adds |
| `docs`     | Documentation only                      |
| `style`    | Formatting, missing semicolons, etc.    |
| `test`     | Adding or fixing tests                  |
| `chore`    | Build, CI, dependencies                 |

Examples:

```
feat: add team invitation via invite code
fix: prevent duplicate certificate generation
refactor: extract scoring logic into separate service
docs: update API endpoint documentation
```

### Running Tests

```bash
# Backend tests
cd backend
pytest                      # All tests
pytest tests/unit           # Unit tests only
pytest tests/integration    # Integration tests only
pytest --cov=app            # With coverage report

# Frontend type checking
cd frontend
npx tsc --noEmit
```

### Code Style & Linting

**Backend:**

The project uses `black`, `isort`, and `flake8`. Run before committing:

```bash
cd backend
black app tests
isort app tests
flake8 app tests
```

Configuration is in `backend/pyproject.toml` and `backend/.flake8`.

**Frontend:**

```bash
cd frontend
npm run lint
```

TypeScript strict mode is enabled. Run `npx tsc --noEmit` to verify.

---

## How to Contribute

### Reporting Bugs

Open a [GitHub Issue](https://github.com/mohamedsillahhh-cloud/hackhub-platform/issues) with:

- A clear, descriptive title
- Steps to reproduce (include code/screenshots if applicable)
- Expected vs actual behaviour
- Environment details (OS, browser, Python/Node versions)

### Suggesting Features

Open a [GitHub Issue](https://github.com/mohamedsillahhh-cloud/hackhub-platform/issues) with:

- A clear, descriptive title prefixed with `[Feature]`
- Use case and motivation
- Proposed solution (optional)

### Opening a Pull Request

1. **Find or create an issue** — comment to let others know you're working on it.
2. **Fork the repository** and create your branch from `main`.
3. **Write clean code** following the project's conventions (Clean Architecture, async/await, typed).
4. **Add tests** for new functionality. Bug fixes should include a test that reproduces the bug.
5. **Ensure CI passes** — run the full test suite and linters.
6. **Keep PRs focused** — one feature/fix per PR. Large changes should be discussed first.
7. **Write a descriptive PR title** following the commit convention (e.g., `feat: add team invitation via invite code`).
8. **Reference the issue** in the PR description using `Closes #123`.

PR checklist before submitting:

- [ ] Code follows existing style and architecture
- [ ] Tests pass (`pytest` + `npx tsc --noEmit`)
- [ ] Linting passes (`black`, `isort`, `flake8`, `npm run lint`)
- [ ] New endpoints have Pydantic `response_model`
- [ ] New database models include Alembic migration
- [ ] Environment variables have defaults and are documented in `.env.example`
- [ ] Frontend hooks follow TanStack Query patterns
- [ ] No `console.log`, debug code, or commented-out code

---

## Architecture & Design Decisions

- **Clean Architecture**: endpoints → services → repositories. Services contain business logic, repositories handle data access. Endpoints are thin.
- **Async everywhere**: Python uses `async/await` with SQLAlchemy 2.0's async session.
- **JWT via httpOnly cookies**: tokens are never exposed to JavaScript. The `access_token` cookie is sent with every request automatically.
- **Rate limiting**: AI endpoints are protected by `slowapi` with per-user limits. Daily token caps tracked in Redis.
- **File structure**: one file per domain in `endpoints/`, `services/`, and (if needed) `repositories/`. Models and schemas are similarly split.
- **Frontend state**: Zustand for auth (cookie-driven, no token in JS), TanStack Query for all server state.

---

*Developed by [Mohamed Sillah](https://github.com/mohamedsillahhh-cloud)*
