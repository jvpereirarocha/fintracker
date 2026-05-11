# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the app (Docker):**
```bash
docker compose up --build
```
This starts the FastAPI app on port 8008, PostgreSQL on 5433, Prometheus on 9090, and Grafana on 3005.

**Run migrations:**
```bash
alembic upgrade head
```

**Create a migration:**
```bash
alembic revision --autogenerate -m "description"
```

**Run locally (without Docker):**
```bash
uvicorn app.main:app --reload
```

**Run tests:**
```bash
pytest
```

**Run a single test file:**
```bash
pytest tests/test_usecase_list_transactions.py
```

**Lint and format:**
```bash
ruff check . --fix
ruff format .
```

**Type check:**
```bash
mypy .
```

**Pre-commit hooks** (ruff lint, ruff format, mypy) run automatically on commit. Install with:
```bash
pre-commit install
```

## Architecture

This is a Python 3.12 / FastAPI backend following a clean architecture pattern with four layers:

### `app/domain/`
The pure business layer — no framework or infrastructure dependencies.
- `entities/` — dataclasses representing domain objects (`TransactionEntity`, `UserEntity`, `CategoryEntity`)
- `value_objects/` — immutable types used as inputs/outputs across layers (filters, pagination, JWT payload, dashboard values)
- `abstractions/` — Protocol-based interfaces for repositories (`AbstractTransactionRepository`, etc.) and an ABC for use cases (`AbstractUseCase`)
- `exceptions/` — domain exceptions that extend `BaseDomainException`, tagged with an `ExceptionType` enum (BAD_REQUEST, NOT_FOUND, etc.) which the API layer maps to HTTP status codes
- `business_logic/` — pure functions for validation and conversion

### `app/usecases/`
One class per use case, all extending `AbstractUseCase` with an async `execute()` method. Each use case receives repository abstractions via constructor injection. Validation and authorization logic lives here (e.g., checking user existence before fetching their transactions).

### `app/infra/`
Concrete implementations of domain abstractions:
- `repositories/` — SQLAlchemy implementations (`AdapterTransactionRepo`, `AdapterUserRepo`, `AdapterCategoryRepo`)
- `database/` — SQLAlchemy ORM models, engine, and session factory; migrations live under `migrations/versions/`
- `auth/` — JWT token provider and bcrypt password handler
- `configs/settings.py` — pydantic-settings `Settings` class reads from `.env`

### `app/api/`
FastAPI layer wiring everything together:
- `v1/endpoints/` — routers per resource (transactions, categories, users, dashboards)
- `v1/dtos/` — Pydantic request/response models (separate from domain entities)
- `dependencies/` — FastAPI `Depends` factories that construct use case instances with the correct repos and inject the current user from the JWT
- `handlers.py` — global exception handlers: `BaseDomainException` → HTTP 4xx, uncaught exceptions → HTTP 500

### Request flow
```
Endpoint → Dependency (builds use case) → UseCase.execute() → Repository → DB
                                                ↓
                                      Domain Exception → API handler → HTTP response
```

### Key conventions
- Repository adapters are named `Adapter<Resource>Repo` and live in `app/infra/repositories/`
- Use cases receive only abstract repository types — never concrete infra classes
- The JWT subject (`sub`) carries the username; endpoints pull the current user from `request.state.user` (set by the `get_current_user` dependency)
- Commits follow Conventional Commits; `python-semantic-release` automates versioning and CHANGELOG updates on the `main` branch
- Line length is 100; mypy runs in strict mode
