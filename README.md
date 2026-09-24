<div align="center">
  <img src="assets/logo.svg" alt="HackHub Logo" width="120" height="120" />
  <h1>HackHub</h1>
  <p>Open-source hackathon management platform.</p>
</div>

HackHub combines a Next.js frontend with a FastAPI API for running events,
forming teams, submitting projects, judging entries, publishing rankings and
issuing verifiable PDF certificates. The project has a deployment-ready
baseline for a controlled single-instance installation; see
[Current status](#current-status) for the operational boundaries.

## Current status

Implemented:

- revocable JWT sessions through HTTP-only access and rotating refresh cookies
- user profiles and admin, organizer, judge and participant roles
- event management and controlled lifecycle transitions
- team creation, actionable invitations, invite codes and leadership transfer
- challenge categories, weighted criteria and project submissions
- judge evaluations, rankings and an SSE ranking stream
- notifications, dashboards and CSV/XLSX exports
- PDF certificates with QR verification and tamper detection
- optional OpenAI-backed assistant and project feedback

Known boundaries:

- SQLite is the supported database for the current single-instance setup.
- Redis is optional; ranking falls back to uncached database queries.
- certificate authenticity uses a server-side keyed hash; PDFs are not signed
  with a public-key document signature.
- push delivery, billing, custom domains and distributed workers are not
  implemented.
- SMTP, Telegram and OpenAI paths require provider credentials and staging
  validation before a production launch.

The durable internal map is in [`MEMORIA/INDEX.md`](MEMORIA/INDEX.md).

## Stack

| Area     | Technologies                                                               |
| -------- | -------------------------------------------------------------------------- |
| Frontend | Next.js 16, React, TypeScript, Tailwind, Radix UI, TanStack Query, Zustand |
| Backend  | FastAPI, SQLAlchemy async, Pydantic, JWT, SlowAPI                          |
| Data     | SQLite with aiosqlite; optional Redis cache                                |
| Tooling  | pytest, black, flake8, ESLint, TypeScript, Docker Compose, Nginx           |

## Quick start

Requirements: Python 3.12+ and Node.js 20+. Redis and Docker are optional.

```bash
git clone https://github.com/mohamedsillahhh-cloud/hackhub-platform.git
cd hackhub-platform

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`, the API at
`http://localhost:8000`, and Swagger at `http://localhost:8000/docs`.
In development, missing SQLite tables may be created on startup. Keep
`alembic upgrade head` in the startup sequence so local and deployed schemas
follow the same versioned path.

To run the full stack through Docker:

```bash
docker compose up --build
```

Nginx exposes the application at `http://localhost`.

## Configuration

The complete development defaults live in `backend/.env.example` and
`frontend/.env.example`. Important backend settings:

| Variable             | Purpose                                                  |
| -------------------- | -------------------------------------------------------- |
| `DATABASE_URL`       | SQLAlchemy async URL; defaults to local SQLite           |
| `SECRET_KEY`         | JWT/signature secret; use at least 32 random characters  |
| `APP_URL`            | Public frontend origin used in links and QR codes        |
| `CORS_ORIGINS`       | Comma-separated trusted browser origins                 |
| `TRUSTED_HOSTS`      | Comma-separated HTTP Host allowlist                     |
| `AUTO_CREATE_TABLES` | Development convenience; must be `false` in production  |
| `REDIS_URL`          | Optional ranking cache and AI usage counters             |
| `OPENAI_API_KEY`     | Optional AI provider credential                          |
| `SMTP_*`             | Optional email transport                                 |
| `TELEGRAM_BOT_TOKEN` | Optional Telegram delivery credential                    |

`ENVIRONMENT=production` additionally requires HTTPS origins, a strong secret
and migrations instead of startup table creation. Readiness is exposed at
`/health/ready`; liveness is exposed at `/health/live`.

## Database operations

Alembic owns persistent schema changes. The backend container detects a legacy
pre-Alembic SQLite database, stamps its known baseline and then upgrades it.
Back up the database before every deployment:

```bash
python scripts/backup_sqlite.py backend/hackhub.db backups
cd backend
alembic upgrade head
alembic check
```

The backup command uses SQLite's online backup API and verifies the resulting
file with `PRAGMA integrity_check`.

## Project structure

```text
backend/app/
  api/v1/endpoints/  HTTP routes
  core/              configuration, database, auth dependencies
  models/            SQLAlchemy models
  schemas/           Pydantic API contracts
  services/          domain rules
  repositories/      reusable data access
frontend/src/
  app/                Next.js routes
  components/         UI and domain components
  hooks/              TanStack Query hooks
  lib/api.ts          Axios API client
  store/              Zustand state
MEMORIA/              durable project knowledge
```

## Verification

```bash
cd backend
pytest -q
alembic -x database_url=sqlite+aiosqlite:///./migration-test.db upgrade head
alembic -x database_url=sqlite+aiosqlite:///./migration-test.db check
black --check app tests alembic --line-length=120
isort --check-only app tests alembic --profile black
flake8 app tests alembic --max-line-length=120 --extend-ignore=E203,W503
pip-audit -r requirements-dev.txt

cd ../frontend
npm run lint
npm run typecheck
npm run build
npm audit --omit=dev --audit-level=high

cd ..
bash scripts/check-memoria.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change.

## License

MIT. See [LICENSE](LICENSE).
