# PB-005: Configuration Management with pydantic-settings

**Sprint:** 1 — Project Foundation & Infrastructure
**Priority:** Critical
**Estimate:** 1 pt
**Status:** In Progress

**As a** developer, **I want** type-safe configuration from environment variables, **so that** settings are validated at startup and I can easily switch between local, test, and Docker environments.

---

## Step 1: Create `app/core/config.py`

Create the file at: `~/privacy-rights-api/app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    APP_TITLE: str = "Privacy Rights API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/privacy_rights"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    API_KEY_PREFIX: str = "pra_live_"


settings = Settings()
```

**Key design decisions:**

- `model_config = SettingsConfigDict(...)` is the Pydantic v2 way to configure settings (replaces the old `class Config` inner class)
- `env_file=".env"` — loads from `.env` file in the project root, but environment variables always take precedence
- `case_sensitive=False` — `database_url` and `DATABASE_URL` both work
- `DATABASE_URL` uses the `postgresql+asyncpg://` scheme — this is what SQLAlchemy async requires (not `postgres://` or `postgresql://`)
- The module-level `settings = Settings()` creates a singleton. Import it anywhere with `from app.core.config import settings`

---

## Step 2: Create `.env` for Local Development

Create the file at: `~/privacy-rights-api/.env`

```env
# Application
DEBUG=true
LOG_LEVEL=DEBUG

# Database (local Docker PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/privacy_rights

# Redis (local Docker Redis)
REDIS_URL=redis://localhost:6379/0
```

**Important:** This file is already in `.gitignore` — it will NOT be committed. This is intentional since `.env` can contain secrets.

---

## Step 3: Create `.env.example` (Committed Template)

Create the file at: `~/privacy-rights-api/.env.example`

```env
# Application
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/privacy_rights

# Redis
REDIS_URL=redis://localhost:6379/0
```

This file IS committed to git so other developers know what variables are needed.

---

## Step 4: Wire Settings into `app/main.py`

Update `app/main.py` to use the settings:

```python
from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_TITLE,
    description="GDPR/CCPA Data Subject Request Service",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
)


@app.get("/")
async def root():
    return {"service": settings.APP_TITLE, "version": settings.APP_VERSION}
```

**What changed:**
- Imported `settings` from `app.core.config`
- `title`, `version`, and `debug` are now driven by config instead of hardcoded strings
- The root endpoint also uses settings values

---

## Step 5: Verify

```bash
cd ~/privacy-rights-api

# Start the app — should pick up .env values
uvicorn app.main:app --reload
```

1. Visit `http://127.0.0.1:8000` — should return:
   ```json
   {"service": "Privacy Rights API", "version": "1.0.0"}
   ```

2. Test that environment variables override `.env`:
   ```bash
   APP_TITLE="My Custom Title" uvicorn app.main:app --reload
   ```
   Visit `http://127.0.0.1:8000` — should return:
   ```json
   {"service": "My Custom Title", "version": "1.0.0"}
   ```

3. Verify linting:
   ```bash
   ruff check .
   ruff format .
   ```

---

## Step 6: Verify Settings Validation

Test that invalid settings are caught at startup. Temporarily add a bad value:

```bash
DATABASE_URL="not-a-url" uvicorn app.main:app --reload
```

The app should still start (we're not validating URL format, just that the string exists). This is fine — the actual connection will fail later when we try to connect, which gives a clearer error. If you want stricter validation, we can add it in a future story.

---

## Acceptance Checklist

- [x] `app/core/config.py` created with `Settings` class using pydantic-settings
- [x] Settings include: `APP_TITLE`, `APP_VERSION`, `DEBUG`, `LOG_LEVEL`, `DATABASE_URL`, `REDIS_URL`, `API_KEY_PREFIX`
- [x] `.env` file created for local development (not committed)
- [x] `.env.example` created as a committed template
- [x] `app/main.py` uses `settings` instead of hardcoded values
- [x] App starts and reads from `.env`
- [x] Environment variables override `.env` values
- [x] `ruff check .` and `ruff format .` pass clean

---

## Next Story

After peer review, proceed to **PB-003** (Async SQLAlchemy + asyncpg database connection), which depends on `settings.DATABASE_URL` from this story.
