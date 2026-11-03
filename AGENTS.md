# Architecture Overview

This is a basic personal SaaS project.

Code management will follow a monorepo strategy to keep all services versioned together, simplify integration, and standardize CI/CD.

The product is focused on work time management with gamified elements.
Users can set up pomodoro timer settings, view their money earned progress,
and get notified when a timer is completed. Binding timers to tasks is a future feature.

## Test-Driven Development (TDD)

- Write tests for every new feature before implementation (pytest for backend, Jest/React Native Testing Library for mobile)
- Code must pass all tests before being merged or deployed
- Maintain minimum test coverage threshold (target: >80%)
- Tests are the primary specification and documentation for expected behavior
- Failed tests block feature acceptance
- Testing applies to all services: backend and mobile

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
   - Domain-Driven Design (DDD) for business modules and boundaries
   
## DDD Approach (Backend)

- Organize code by domain (not by technical layer only)
- Each domain contains its own application, domain models, schemas, and infrastructure concerns
- Keep business rules in domain services/entities and keep API routers thin
- Use repositories/adapters for external systems (database, third-party APIs)
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
| password_hash | str         | bcrypt hash (`bcrypt` lib, cost factor 12). Never store or return the raw password. bcrypt only uses the first 72 bytes, so reject passwords longer than 72 bytes (UTF-8) with a 422 |
| is_active     | bool        | Default `true`; inactive users cannot authenticate (ban/disable). Not a soft delete: "Delete account" is a hard delete |

### RefreshToken (`auth` context) — inherits BaseEntity

Persisted so tokens can be revoked. Access tokens are short-lived JWTs and are not stored.

| Field      | Type     | Notes                                          |
|------------|----------|------------------------------------------------|
| user_id    | UUID     | FK → User.id, `ON DELETE CASCADE`              |
| token_hash | str      | Hash of the refresh token; never store it raw  |
| expires_at | datetime | UTC                                            |
| revoked_at | datetime | UTC, null while valid; set on logout/rotation  |

### Cashdoro (`cashdoro` context) — inherits BaseEntity

Timer settings owned by a user. For now a user has exactly **one** cashdoro (1:1, created with defaults and edited afterwards). Future feature: a user may have several, each bound to a contact.

| Field                     | Type     | Notes                                      |
|---------------------------|----------|--------------------------------------------|
| user_id                   | UUID     | FK → User.id, unique (1:1 for now), `ON DELETE CASCADE` |
| session_time              | int      | Focus duration, in minutes. Default `25`. Range `1–180` |
| pause_time                | int      | Short break duration, in minutes. Default `5`. Range `1–60` |
| long_pause_time           | int      | Long break duration, in minutes. Default `15`. Range `1–120` |
| sessions_until_long_break | int      | Focus phases before a long break. Default `4`. Range `1–12` |
| hourly_rate               | Decimal  | `Numeric(12, 2)`, nullable, default `null`. Money earned per hour of focus; `null` = free sessions (plain pomodoro, no earnings). Range `0–100000.00` |
| total_earnings            | Decimal  | `Numeric(12, 2)`, sum of session earnings, default `0`; never use float |

Out-of-range values are rejected with a validation error (422).

Cashdoro holds **current settings only**; it is not history. Editing it never changes past sessions.
`total_earnings` is a cached total: update it in the same transaction that ends a focus phase with earnings so it never drifts from the sum of `Session.earnings`.

### Session (`sessions` context) — inherits BaseEntity

One row per pomodoro run: a **focus** phase followed by a **break** phase (short or long). Session rows **are** the history. Settings are snapshotted at start so later cashdoro edits do not rewrite past earnings.

| Field          | Type     | Notes                                          |
|----------------|----------|------------------------------------------------|
| cashdoro_id    | UUID     | FK → Cashdoro.id, `ON DELETE CASCADE`          |
| phase          | enum     | `focus` / `short_break` / `long_break`; current phase while running, last phase reached once ended |
| started_at     | datetime | UTC, start of the focus phase                  |
| focus_ended_at | datetime | UTC, null while in focus; start of the break   |
| ended_at       | datetime | UTC, null while running                        |
| session_time   | int      | Snapshot of planned focus minutes at start     |
| break_time     | int      | Planned break minutes; set when the break starts (`pause_time` or `long_pause_time`) |
| hourly_rate    | Decimal  | `Numeric(12, 2)`, snapshot of the cashdoro rate at start; `null` = free session |
| focus_seconds  | int      | Actual focused time (may be < planned); set when focus ends |
| earnings       | Decimal  | `Numeric(12, 2)`, set when focus ends; see rules below |
| status         | enum     | `running` / `completed` / `abandoned` / `canceled` |

Phase rules:
- A session starts in `focus`. When focus ends (time elapsed or skipped), it moves to a break.
- The break is `long_break` when this focus is the `sessions_until_long_break`-th focus counted since the last long break; otherwise `short_break`. Only sessions that reached a break count (`abandoned` in focus and `canceled` sessions do not). The count resets to zero when more than 24 hours have passed since the `focus_ended_at` of the last counted session.
- When the break ends (time elapsed), the session becomes `completed`. The next session starts when the user starts it, except on skip (see Services).
- Phase transitions on elapsed time are applied by the backend lazily on any read or write of the session (no background job), using the planned end time, not the request time.
- Lazy transitions live in a single domain method (e.g. `Session.advance(now)`); no other code changes `phase`/`status` based on elapsed time.
- A session is started from **one place only**: the `StartSession` use case. It first loads the cashdoro's `running` session and calls `advance(now)` on it, and only then checks the "one running session" rule. Every path that starts a session (Start session, skip in a break) goes through it; no other code creates `Session` rows.

Earnings rules:
- Earnings are calculated in the domain layer and stored when the focus phase ends; they are never recalculated afterwards.
- Rounding: all money values have 2 decimal places, rounded with `ROUND_HALF_EVEN` (banker's rounding) via `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)`. Round each session's `earnings` once, then add the rounded value to `total_earnings`.
- Focus ended by elapsed time, skip, or abandon: `earnings = focus_seconds / 3600 × hourly_rate`, where `focus_seconds` is the time focused until that moment (capped at `session_time × 60`).
- `canceled`: `earnings = 0`, nothing is added to `total_earnings`.
- Free session (`hourly_rate` is `null`): `earnings` is `null`, nothing is added to `total_earnings`.
- History = sessions of the user's cashdoro ordered by `started_at` desc.

Relationships: `User 1 ── 1 Cashdoro` (will become `1 ── N`), `User 1 ── N RefreshToken`, `Cashdoro 1 ── N Session`.

## Services

### Backend (`apps/backend`)

The backend is the source of truth for the session timer and its phases. The mobile app never sends durations.

All routes are served under the `/api/v1` prefix.

#### `auth`
- **Register**: creates the user and its default cashdoro (25 min session, 5 min short break, 15 min long break every 4 sessions, no hourly rate) in the same transaction, calling `cashdoro.application`.
- **Login**: rejects users with `is_active = false`. Returns a short-lived access token (default 15 minutes) and a refresh token (default 7 days). Both lifetimes are configurable via settings.
- **Refresh token**: exchanges a valid refresh token for a new pair; the old refresh token is revoked (rotation).
- **Logout**: revokes the refresh token. The access token expires on its own shortly after.
- **Current user (dependency)**: `get_current_user` validates the access token, then loads the user by `sub`; returns 401 if the user no longer exists or has `is_active = false`. This cuts off banned/deleted users without storing access tokens.
- **Get me**: returns the authenticated user (never the password hash).
- **Delete account**: hard delete of the user; its cashdoro, sessions, and refresh tokens are removed by `ON DELETE CASCADE`.

#### `cashdoro`
- **Get cashdoro**: returns the user's cashdoro settings and `total_earnings`.
- **Update cashdoro**: edits session, short/long break durations, sessions until long break, and `hourly_rate` (may be set to `null` to switch to free sessions).

#### `sessions`
- **Start session**: snapshots `session_time` and `hourly_rate` from the cashdoro, sets `started_at = now` (UTC), phase `focus`, status `running`. Only one `running` session per cashdoro at a time.
- **Get running session**: returns the running session with its `phase`, `elapsed_seconds` and `remaining_seconds` for the current phase, computed by the backend.
- **Skip phase**:
  - In `focus`: ends focus now, computes `focus_seconds` and `earnings` until this moment, adds them to `Cashdoro.total_earnings` in the same transaction, and starts the break (short or long).
  - In a break: ends the session as `completed` and immediately starts the next session in `focus` by calling the `StartSession` use case.
- **Abandon session**: stops the cycle. In `focus`, ends focus now and keeps the partial `earnings` (added to `total_earnings`). In a break, earnings were already set. Status `abandoned`.
- **Cancel session**: only in `focus`. Ends the session with `earnings = 0`; `total_earnings` is unchanged. Status `canceled`.
- **List past sessions of a cashdoro**: ordered by `started_at` desc.

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
