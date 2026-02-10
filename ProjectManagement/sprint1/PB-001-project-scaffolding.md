# PB-001: Project Scaffolding

**Sprint:** 1 — Project Foundation & Infrastructure
**Priority:** Critical
**Estimate:** 2 pts
**Status:** In Progress

**As a** developer, **I want** a properly structured FastAPI project with dependency management, **so that** I can start building features on a solid foundation.

---

## Step 1: Create the Directory Structure

Create the following directories with empty `__init__.py` files where indicated:

```
privacy-rights-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── middleware/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── alembic/           (empty for now, configured in PB-004)
├── Docs/
│   └── SRS.md         (already exists)
├── ProjectManagement/ (already exists)
└── pyproject.toml
```

**Commands:**

```bash
cd ~/privacy-rights-api

# App package and subpackages
mkdir -p app/api/v1 app/core app/middleware app/models app/schemas app/services

# Test package
mkdir -p tests

# Alembic directory (placeholder)
mkdir -p alembic

# Create all __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/core/__init__.py
touch app/middleware/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch tests/__init__.py
```

**Purpose of each directory:**

| Directory | Responsibility |
|-----------|---------------|
| `app/api/v1/` | Route handlers (routers) for API v1 endpoints |
| `app/core/` | Configuration, database connection, Redis connection |
| `app/middleware/` | Auth middleware, tenant scoping, audit logging |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response schemas |
| `app/services/` | Business logic (DSR processing, consent management) |
| `tests/` | All pytest tests |
| `alembic/` | Database migration scripts |

---

## Step 2: Create `pyproject.toml`

Create the file at the project root: `~/privacy-rights-api/pyproject.toml`

```toml
[project]
name = "privacy-rights-api"
version = "1.0.0"
description = "GDPR/CCPA Data Subject Request Service"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "redis>=5.0.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.4.0",
    "pytest-cov>=5.0.0",
]

[tool.setuptools.packages.find]
include = ["app*"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Key notes:**

- `sqlalchemy[asyncio]` — pulls in the greenlet async extras needed for async sessions
- `redis>=5.0.0` — includes `redis.asyncio` built-in (no separate `aioredis` package needed)
- `python-multipart` — required by FastAPI for form/multipart request parsing
- `asyncio_mode = "auto"` — pytest-asyncio auto-detects async test functions, so you don't need `@pytest.mark.asyncio` on every test
- Ruff rules selected:
  - `E`/`F` — pycodestyle errors + pyflakes
  - `I` — isort (import sorting)
  - `N` — pep8-naming
  - `W` — pycodestyle warnings
  - `UP` — pyupgrade (modernize syntax)
  - `B` — flake8-bugbear (common bugs)
  - `SIM` — flake8-simplify

---

## Step 3: Create `app/main.py`

Create the file at: `~/privacy-rights-api/app/main.py`

```python
from fastapi import FastAPI

app = FastAPI(
    title="Privacy Rights API",
    description="GDPR/CCPA Data Subject Request Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    return {"service": "Privacy Rights API", "version": "1.0.0"}
```

**Notes:**
- This is the minimal entry point. Routers, middleware, and startup/shutdown events will be added in later stories.
- `docs_url="/docs"` and `redoc_url="/redoc"` are the defaults but we set them explicitly for clarity.

---

## Step 4: Install Dependencies and Verify

```bash
cd ~/privacy-rights-api

# Install the project in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify the app starts
uvicorn app.main:app --reload
```

**Verification:**

1. Visit `http://127.0.0.1:8000` — should return:
   ```json
   {"service": "Privacy Rights API", "version": "1.0.0"}
   ```

2. Visit `http://127.0.0.1:8000/docs` — should show the Swagger UI with the root endpoint listed.

3. Visit `http://127.0.0.1:8000/redoc` — should show the ReDoc alternative.

Press `Ctrl+C` to stop the server.

---

## Step 5: Verify Linting

```bash
cd ~/privacy-rights-api

# Check for lint errors
ruff check .

# Format code
ruff format .
```

Both commands should pass cleanly with no errors or changes needed.

---

## Acceptance Checklist

- [x] Directory structure created with all `__init__.py` files
- [x] `pyproject.toml` created with all dependencies and tool configuration
- [x] `app/main.py` creates FastAPI app with title, description, version
- [x] `pip install -e ".[dev]"` succeeds without errors
- [x] `uvicorn app.main:app --reload` starts and `GET /` returns JSON
- [x] `http://127.0.0.1:8000/docs` shows Swagger UI
- [x] `ruff check .` passes clean
- [x] `ruff format .` passes clean

---

## Next Story

After peer review, proceed to **PB-005** (Configuration management with pydantic-settings), since PB-003 (database setup) and PB-004 (Alembic) depend on configuration being in place first.
