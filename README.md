# Cashdoro

A pomodoro timer that shows what your focus time is worth.

Set your focus and break durations and an hourly rate, and Cashdoro tracks how much each focus session earned. Earnings are a progress indicator based on your own rate: the app does not pay real money.

## Status

Early development. Only the backend foundation exists today.

| Area | State |
|---|---|
| Health check | Done |
| Auth: register, login, refresh, logout | Done |
| Account: get and delete current user | Done |
| `cashdoro` context: timer settings and earnings | Planned |
| `sessions` context: timer phases and history | Planned |
| Mobile app, shared types, CI | Planned |

## Stack

**Current**

- Python 3.14+ and FastAPI, with sync endpoints
- PostgreSQL, SQLAlchemy with psycopg, and Alembic
- Pydantic v2 for validation and settings
- JWT access tokens and bcrypt password hashing
- uv, pytest, and ruff

**Planned**

- Expo, React Native, and NativeWind

## Project structure

```text
apps/backend/
  alembic/         # Database migrations
  src/
    main.py        # App factory and router registration
    shared/        # Config, database, security, common dependencies
    auth/          # Bounded context
      domain/          # Entities and repository protocols
      application/     # Use cases and DTOs
      infrastructure/  # SQLAlchemy models and repositories
      api/             # Routers and request/response schemas
  tests/
    api/           # Main suite: HTTP tests against a real Postgres
    unit/          # Reserved for pure domain rules
infra/docker/      # Docker Compose file
```

## Engineering practices

### `AGENTS.md` as the project spec

[`AGENTS.md`](AGENTS.md) is the single source of truth for architecture, models, business rules, and conventions. Both people and AI coding agents work from it, so decisions stay consistent and features are specified before they are built.

### Domain-Driven Design

Code is organized by business context rather than by technical layer alone. `auth` is implemented, and `cashdoro` and `sessions` are planned.

Each context owns four layers:

- **`domain`:** business rules in pure Python, with no FastAPI or SQLAlchemy
- **`application`:** one use case per user action
- **`infrastructure`:** ORM models and repository implementations
- **`api`:** thin routers that parse a request, call a use case, and map the response

This keeps business rules independent of the framework and the database.

### Test-Driven Development

Tests are written before the implementation and act as its specification, so the code changes to satisfy them, not the other way around.

- **`tests/api/`** is the main suite. It uses FastAPI's `TestClient` against a real Postgres, covering router, use case, repository, and database in one pass.
- **`tests/unit/`** is reserved for pure domain rules, without mocked repositories. It has no tests yet.
- **Coverage** must stay at 80% or higher, enforced through the pytest-cov configuration.

### Design patterns

- **Repository with `typing.Protocol`:** the domain declares what it needs, and infrastructure implements it.
- **Use case:** a class with an `execute` method, such as `LoginUser` or `RefreshTokens`, orchestrates each action.
- **Data Mapper:** ORM models stay separate from domain entities, and repositories convert between them.
- **Dependency injection:** FastAPI's `Depends` handles the wiring, with no container library.

New patterns are added only when there is a concrete need, to avoid overengineering.

### Technical decisions

- **Sync-only backend:** async would add complexity this app does not need.
- **Short-lived JWTs with refresh tokens:** refresh tokens are stored only as hashes, can be revoked, and are rotated on every use.
- **Versioned migrations:** every schema change goes through Alembic.

### Workflow

The repository is a monorepo that follows trunk-based development, with short-lived feature branches and [Conventional Commits](https://www.conventionalcommits.org/).

### Specified but not yet implemented

These rules are defined in `AGENTS.md` and will arrive with the `cashdoro` and `sessions` contexts:

- Earnings calculated with `Decimal` and `ROUND_HALF_EVEN`
- Settings snapshotted per session, so later edits do not rewrite past earnings
- Timer phases computed by the backend, as the source of truth

## Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/)
- PostgreSQL, installed natively or through Docker

### 1. Set up the database

Choose one option.

**Native PostgreSQL**

```bash
psql -U postgres -c "CREATE ROLE cashdoro WITH LOGIN CREATEDB PASSWORD 'cashdoro';"
psql -U postgres -c "CREATE DATABASE cashdoro OWNER cashdoro;"
```

The role needs `CREATEDB` because the test suite creates its own `cashdoro_test` database.

**Docker Compose**

Run this from the repository root. Port 5432 must be free, so stop any native PostgreSQL first.

```bash
docker compose -f infra/docker/compose.yml up -d
```

### 2. Configure the environment

Run the remaining commands from `apps/backend`.

```bash
cd apps/backend
cp .env.example .env
openssl rand -hex 32  # Paste the result into JWT_SECRET in .env
```

The defaults in `.env.example` match both database options above. These optional variables can also be set in `.env`:

| Variable | Default |
|---|---|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |

### 3. Install, migrate, and run

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/v1/health>

All routes are served under `/api/v1`.

## Tests and linting

Run these from `apps/backend`, with PostgreSQL running.

```bash
uv run pytest                 # Run the tests
uv run pytest --cov           # Run the tests with coverage
uv run ruff check .           # Lint
uv run ruff format --check .  # Check formatting
```

## License

This is proprietary software, and all rights are reserved. See [`LICENSE`](LICENSE).
