# Architecture Overview

This is a SaaS basic personal project. 

Code management will follow a monorepo strategy to keep all services versioned together, simplify integration, and standardize CI/CD.

The product is focused in work time management with gamified elements.
User can setup pomodoro timer settings and bind with tasks, view money
earned progress and get notified when one timer is completed.

## Test-Driven Development (TDD)

- Write tests for every new feature before implementation (pytest for backend, Jest/React Native Testing Library for mobile)
- Code must pass all tests before being merged or deployed
- Maintain minimum test coverage threshold (target: >80%)
- Tests are the primary specification and documentation for expected behavior
- Failed tests block feature acceptance
- Testing applies to all services: backend, frontend, and mobile (when implemented)

### Backend test strategy

- **API tests (`tests/api/`) are the main suite.** They hit endpoints through the FastAPI test client against a real Postgres, covering router → use case → repository → DB in one pass. Most features (CRUD, auth, transactions like keeping `total_earnings` in sync) are tested here.
- **Unit tests (`tests/unit/`) are only for pure domain rules**, e.g. the earnings calculation (`Decimal` precision/rounding) and session status transitions. They are fast, need no fixtures, and must not mock repositories.
- No separate integration folder. Add one only if a repository gains complex queries worth testing in isolation.
- **Tests written before implementation must never be modified, under any circumstances.** They are the specification: the implementation must be changed to make them pass, never the other way around. This includes weakening assertions, skipping, deleting, or marking them as expected failures.

## Monorepo Strategy

- Single repository for backend and mobile
- Shared standards for linting, formatting, commit conventions, and CI pipelines
- Shared contracts (API schemas, DTOs, and docs) to reduce frontend/backend drift
- Independent deployability per service, even with one repository
- Trunk-based development with short-lived feature branches

## Stack

1. Mobile App
   - Gamified mobile frontend for project (Expo, React Native, NativeWind)
   - Animations and sensory feedback libraries (Lottie, Reanimated, Confetti, Haptics)
2. Backend API
   - Python with **FastAPI** (async request handling, automatic OpenAPI/Swagger docs)
   - JWT tokens for user sessions (OAuth2 with Password Flow / JWT)
   - PostgreSQL database with SQLAlchemy (ORM) + Alembic (migrations)
   - Pydantic v2 for data validation and DTO schemas
   - Local MinIO for object storage
   - Domain-Driven Design (DDD) for business modules and boundaries
   
## DDD Approach (Backend)

- Organize code by domain (not by technical layer only)
- Each domain contains its own application, domain models, schemas, and infrastructure concerns
- Keep business rules in domain services/entities and keep API routers thin
- Use repositories/adapters for external systems (database, storage MinIO, third-party APIs)
- Bounded contexts: `auth`, `cashdoro` (timer settings + earnings), `sessions`. Add new contexts (e.g. gamification) only when their business rules justify it
- Start simple: apply DDD where business complexity exists; avoid overengineering

## ENV

To be defined.

## Directory Structure

```text
project-s/
   apps/
      backend/           # FastAPI
         alembic/        # Migrations
         alembic.ini
         src/
            main.py      # Entry point: app factory, router registration
            shared/      # Cross-context code (no business rules)
               config.py       # Settings (pydantic-settings, env vars)
               security.py     # JWT encode/decode, password hashing
               database.py     # Async engine, session factory, BaseEntity
               dependencies.py # Common FastAPI deps (db session, current user)
            auth/        # Bounded context (same layout for every context)
               domain/          # Entities, value objects, repository protocols
               application/     # Use cases + use-case DTOs
               infrastructure/  # SQLAlchemy models, repository implementations
               api/             # FastAPI router + request/response schemas
            cashdoro/
               domain/ application/ infrastructure/ api/
            sessions/
               domain/ application/ infrastructure/ api/
         tests/
            unit/        # Pure domain rules only, no DB, no mocks (mirrors src/<context>/domain/)
            api/         # Main suite: HTTP via FastAPI test client against a real Postgres
      mobile/            # App frontend (Expo + React Native)
   packages/
      shared-types/      # Contracts and shared schemas / OpenAPI types
   infra/
      docker/            # Docker and compose files
      ci/                # CI pipeline definitions
   docs/
      architecture/
      api/
```

### Layer dependency rules (backend)

Each bounded context lives in its own folder under `src/` and owns all of its layers.

- `domain` imports nothing from `application`, `infrastructure`, `api`, FastAPI, or SQLAlchemy. Pure Python.
- `domain` defines repository interfaces as `typing.Protocol`; `infrastructure` implements them.
- `application` depends only on `domain` (and `shared/` config). It orchestrates use cases; business rules stay in `domain`.
- `infrastructure` holds SQLAlchemy ORM models, which are separate from domain entities. Repositories map between them.
- `api` stays thin: parse request → call a use case → map the result to a response schema. No business logic, no direct DB access.
- Contexts do not import each other's `infrastructure` or `api`. Cross-context calls go through the other context's `application` layer.
- `shared/` contains technical plumbing only; no domain concepts.

## Models

### BaseEntity (abstract, `shared/database.py`)

Abstract SQLAlchemy base (`__abstract__ = True`): it has no table of its own. Every ORM model inherits from it and gets these fields; do not redeclare them in subclasses.

| Field      | Type     | Notes                                  |
|------------|----------|----------------------------------------|
| id         | UUID     | PK, generated on insert                |
| created_at | datetime | UTC, set on insert (server default)    |
| updated_at | datetime | UTC, set on insert and on every update |

### User (`auth` context) — inherits BaseEntity

| Field         | Type        | Notes                                  |
|---------------|-------------|----------------------------------------|
| email         | str         | Unique, validated                      |
| username      | str         | Unique                                 |
| password_hash | str         | Never store or return the raw password |
| is_active     | bool        | Default `true`; inactive users cannot authenticate (ban/disable). Not a soft delete: "Delete account" is a hard delete |

### Cashdoro (`cashdoro` context) — inherits BaseEntity

Timer settings owned by a user. For now a user has exactly **one** cashdoro (1:1, created with defaults and edited afterwards). In the future a user may have several, each bound to a contact.

| Field          | Type     | Notes                                      |
|----------------|----------|--------------------------------------------|
| user_id        | UUID     | FK → User.id, unique (1:1 for now)         |
| session_time   | int      | Focus duration, in minutes                 |
| pause_time     | int      | Break duration, in minutes                 |
| hourly_rate    | Decimal  | Money earned per hour of focus             |
| total_earnings | Decimal  | Sum of session earnings; never use float   |

Cashdoro holds **current settings only**; it is not history. Editing it never changes past sessions.
`total_earnings` is a cached total: update it in the same transaction that completes a session so it never drifts from the sum of `Session.earnings`.

### Session (`sessions` context) — inherits BaseEntity

One row per pomodoro run. Session rows **are** the history. Settings are snapshotted at start so later cashdoro edits do not rewrite past earnings.

| Field         | Type     | Notes                                          |
|---------------|----------|------------------------------------------------|
| cashdoro_id   | UUID     | FK → Cashdoro.id                               |
| started_at    | datetime | UTC                                            |
| ended_at      | datetime | UTC, null while running                        |
| session_time  | int      | Snapshot of planned focus minutes at start     |
| hourly_rate   | Decimal  | Snapshot of the cashdoro rate at start         |
| focus_seconds | int      | Actual focused time (may be < planned)         |
| earnings      | Decimal  | `focus_seconds / 3600 × hourly_rate`, set on end |
| status        | enum     | `running` / `completed` / `abandoned`          |

Rules:
- Earnings are calculated in the domain layer and stored when the session ends; they are never recalculated afterwards.
- History = sessions of the user's cashdoro ordered by `started_at` desc.

Relationships: `User 1 ── 1 Cashdoro` (will become `1 ── N`), `Cashdoro 1 ── N Session`.

## Services

### Backend (`apps/backend`)

The backend is the source of truth for the session timer. The mobile app never sends durations.

#### `auth`
- **Register**
- **Login**
- **Logout**
- **Delete account**

#### `cashdoro`
- **Update cashdoro**
- **View total earnings**

#### `sessions`
- **Start session**: snapshots `session_time` and `hourly_rate` from the cashdoro, sets `started_at = now` (UTC) and status `running`. Only one `running` session per cashdoro at a time.
- **Get running session**: returns the running session with `elapsed_seconds` and `remaining_seconds` computed by the backend from `started_at`.
- **Complete session**: only allowed once `session_time` has elapsed. The backend sets `ended_at`, computes `focus_seconds = min(ended_at - started_at, session_time × 60)` and `earnings` in the domain layer, and adds them to `Cashdoro.total_earnings` in the same transaction.
- **Abandon session**: ends a running session early. The backend sets `ended_at` and `focus_seconds` the same way. Whether partial focus time earns money is to be defined.
- **List past sessions of a cashdoro**: ordered by `started_at` desc.
- **See session earnings**

### Mobile (`apps/mobile`)

- **Timer screen**: fetches the running session from the backend to sync the values shown on screen; never computes or sends durations.
- **Notify**: notifies the user when a timer is completed.

## 12 Common Hurdles with Commented Solutions
To be defined.

## 14 Design Patterns
To be defined.

## Weekly Pipeline
To be defined.

## Post-Implementation Checklist
To be defined.
