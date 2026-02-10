# PB-003: Async SQLAlchemy + asyncpg Database Connection

**Sprint:** 1 — Project Foundation & Infrastructure
**Priority:** Critical
**Estimate:** 2 pts
**Status:** In Progress

**As a** developer, **I want** an async database connection pool, **so that** all DB operations are non-blocking.

---

## Step 1: Create `app/core/database.py`

Create the file at: `~/privacy-rights-api/app/core/database.py`

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Key design decisions:**

- `create_async_engine` — uses asyncpg under the hood (driven by the `postgresql+asyncpg://` scheme in `DATABASE_URL`)
- `echo=settings.DEBUG` — logs all SQL queries when DEBUG is true (helpful during development, silent in production)
- `pool_size=10, max_overflow=20` — connection pool holds 10 persistent connections, can grow to 30 under load
- `pool_pre_ping=True` — tests connections before using them (prevents "connection closed" errors after DB restarts)
- `expire_on_commit=False` — after committing, you can still access object attributes without triggering a lazy load (important for async since lazy loading is not supported)
- `Base` — the declarative base class that all SQLAlchemy models will inherit from
- `get_db()` — an async generator dependency for FastAPI. It yields a session, commits on success, and rolls back on exception. FastAPI's `Depends(get_db)` handles the lifecycle automatically.

---

## Step 2: Create `app/models/base.py`

Create the file at: `~/privacy-rights-api/app/models/base.py`

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
```

**Why mixins:**

- Every model in the SRS has `created_at` and `updated_at` TIMESTAMPTZ columns — the `TimestampMixin` avoids repeating this in every model
- Every model except `DSRStatusHistory` and `AuditLog` uses UUID primary keys — the `UUIDPrimaryKeyMixin` standardizes this
- `DateTime(timezone=True)` maps to PostgreSQL `TIMESTAMPTZ` (all timestamps stored in UTC per SRS Section 1.5)
- `server_default=func.now()` — the DB generates the timestamp, not Python (ensures consistency)
- `onupdate=func.now()` — auto-updates `updated_at` on every change

---

## Step 3: Add Startup/Shutdown Events to `app/main.py`

Update `app/main.py` to add lifespan events that manage the database engine:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing needed, engine connects lazily
    yield
    # Shutdown: dispose the connection pool
    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"service": settings.APP_TITLE, "version": settings.APP_VERSION}
```

**What changed:**

- Added `lifespan` async context manager — this is the modern FastAPI way to handle startup/shutdown (replaces the deprecated `@app.on_event("startup")` pattern)
- On shutdown, `engine.dispose()` cleanly closes all connections in the pool
- The engine connects lazily on first use, so no explicit startup action is needed

---

## Step 4: Export Base from `app/models/__init__.py`

Update `~/privacy-rights-api/app/models/__init__.py`:

```python
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["Base", "TimestampMixin", "UUIDPrimaryKeyMixin"]
```

This lets future models import cleanly: `from app.models import Base, TimestampMixin, UUIDPrimaryKeyMixin`

---

## Step 5: Verify

You need a running PostgreSQL to fully test the connection. If you don't have Docker set up yet (PB-002), you can verify the code loads without errors:

```bash
cd ~/privacy-rights-api

# Verify imports work (no connection attempted yet since engine is lazy)
python -c "from app.core.database import engine, async_session_factory, Base, get_db; print('Database module OK')"

# Verify models base imports
python -c "from app.models import Base, TimestampMixin, UUIDPrimaryKeyMixin; print('Models base OK')"

# Verify app still starts
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` — should still return the root response.

```bash
# Lint check
ruff check .
ruff format .
```

---

## Acceptance Checklist

- [x] `app/core/database.py` created with async engine, session factory, `Base`, and `get_db` dependency
- [x] `app/models/base.py` created with `TimestampMixin` and `UUIDPrimaryKeyMixin`
- [x] `app/models/__init__.py` exports `Base`, `TimestampMixin`, `UUIDPrimaryKeyMixin`
- [x] `app/main.py` updated with `lifespan` for engine disposal on shutdown
- [x] `python -c "from app.core.database import ..."` succeeds
- [x] `python -c "from app.models import ..."` succeeds
- [x] App starts with `uvicorn app.main:app --reload`
- [x] `ruff check .` and `ruff format .` pass clean

---

## Next Story

After peer review, proceed to **PB-004** (Alembic migration configuration), which depends on `Base` and the async engine from this story.
