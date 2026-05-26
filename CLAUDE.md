# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package manager

This project uses [uv](https://docs.astral.sh/uv/). Python version is pinned to 3.12 via `.python-version`.

```bash
uv sync                          # install / update dependencies
uv add <package>                 # add a dependency
uv run <command>                 # run a command inside the venv
```

## Running the app

The project root contains `setup.py`, which is **not** a standard packaging file — it is the ASGI app entry point. It adds `src/` to `sys.path`, calls `django.setup()`, and re-exports the FastAPI `app` from `src/main.py`. Always use it when starting the server from the project root:

```bash
uv run uvicorn setup:app --reload
```

Django management commands must be run from inside `src/` (so `core`, `models`, etc. are importable):

```bash
cd src && uv run python core/manage.py migrate
cd src && uv run python core/manage.py makemigrations
cd src && uv run python core/manage.py shell
```

Running `django-admin` from the project root causes `AppRegistryNotReady` because `src/` is not on the Python path.

## Tests and linting

There are no tests or linting tools configured in this project yet (no pytest, ruff, black, etc.).

## Architecture

The project combines **Django** (ORM + migrations) with **FastAPI** (HTTP layer), deployed on **AWS Lambda** via [Mangum](https://mangum.fazecast.com). Django owns models and migrations; FastAPI owns routes and request/response contracts.

```
src/
  core/
    envs.py          # Pydantic-settings classes: Settings, AwsSettings, DatabaseSettings
    config.py        # Django settings — imports from core/envs.py; hardcodes SQLite
    context.py       # permissions_var: ContextVar for per-request permission list
    manage.py        # Django management entry point
  models/
    apps.py          # DatabaseConfig AppConfig — registers the 'models' app with Django
    user.py          # Django ORM models: User, Role, Permission (all inherit BaseModel with UUID PK)
    models.py        # Re-exports User, Role, Permission for convenience
  repositiories/     # Data access layer — wraps Django ORM queries (note: intentional typo in dir name)
  services/          # Business logic layer — calls repositories, calls AWS Cognito
  schemas/
    base.py          # PaginateResponse[T] generic
    user.py          # Input dataclasses and response BaseModels
  routes/
    dependencies.py  # FastAPI DI: get_current_user (JWKS/JWT), get_service
    middlewares.py   # LoggingMiddleware + DecoratorUtil.require_access decorator
    endpoints/       # FastAPI route handlers (CBV pattern via fastapi_utils)
  common/
    enums.py         # StageOption, DatabaseOption
```

### Request flow

`routes/endpoints → services → repositiories → models (Django ORM)`

### Route pattern

Routes use **class-based views** via `fastapi_utils.cbv`, not standard FastAPI function views:

```python
@cbv(router)
class UserRouter:
    service: UserService = Depends(get_service)

    @router.get("/", response_model=PaginateResponse[UserResponse])
    @DecoratorUtil.require_access("some:permission")
    def get_users(self, page: int = 1, page_size: int = 10):
        return self.service.get_users(page, page_size)
```

### Schema pattern

Input schemas are `@dataclass(frozen=True)`; response schemas are `BaseModel` with `from_attributes=True` (for ORM → Pydantic conversion):

```python
@dataclass(frozen=True)
class AddRoleCommand:     # input
    user_id: UUID
    role: str

class RoleResponse(BaseModel):  # output
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
```

### Auth & permissions

- Authentication: Cognito JWT (RS256). `get_current_user` in `dependencies.py` fetches JWKS from Cognito, decodes the token, and reads the `username` claim (not `email`) to look up permissions, which are stored in `permissions_var` (a `ContextVar`).
- The JWKS response is cached via `@lru_cache(maxsize=1)` — restart the server to force a refresh if Cognito keys rotate.
- Authorization: `@DecoratorUtil.require_access("permission:name")` on endpoint methods. Permissions use `:` as the namespace separator. Supports `"*"` (superadmin) and `"module:*"` (module-level wildcard).

### Configuration (`src/core/envs.py`)

Three `pydantic-settings` classes, all reading from `.env` at the project root:

| Class | Purpose |
|---|---|
| `Settings` | Stage, debug flag, API version/prefix, `ROOT_PATH` |
| `AwsSettings` | Cognito, S3, CloudFront signing keys, WebSocket Lambda, ECS reports API, DynamoDB collection names, Redis, SQS queue URLs |
| `DatabaseSettings` | Postgres connection params (parsed but not currently wired into `config.py`) |

`settings.ROOT_PATH` is computed as `/{stage}-tf` (empty string for local).

### Database

- Django settings (`config.py`) currently hardcode **SQLite** for all environments.
- `DatabaseSettings` parses Postgres vars from `.env` but `config.py` does not yet read them — Postgres support is not yet wired up.
- DB timezone is `Etc/GMT+5` (Lima, Peru); app timezone is `America/Lima`.
- All ORM models inherit `BaseModel` (defined in `models/user.py`) which provides a UUID primary key, `created_at`, and `updated_at`.

### Stages

`StageOption` enum: `local`, `test`, `dev`, `qa`, `prod`. Use `stage.is_local_or_test_env()` to branch on local/test behavior.

### Deployment

Mangum wraps the FastAPI `app` for AWS Lambda. The `ROOT_PATH` is `/{stage}-tf` in non-local environments to match the API Gateway stage prefix.

## Environment variables

Create a `.env` file at the project root:

```
STAGE=local
DEBUG=true
DATABASE=sqlite

# Postgres (parsed but not yet active — see Database section)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_NAME=postgres

# Required for auth endpoints (Cognito)
DEPLOY_REGION=
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
COGNITO_CLIENT_SECRET=
```
