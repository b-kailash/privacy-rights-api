# Sprint Board

## Current Sprint: Sprint 1 — Project Foundation & Infrastructure

| Story ID | Story | Status | Notes |
|----------|-------|--------|-------|
| PB-001 | Project scaffolding | Done | Reviewed & approved |
| PB-002 | Docker Compose setup | To Do | |
| PB-003 | Async SQLAlchemy + asyncpg setup | To Do | |
| PB-004 | Alembic migration configuration | To Do | |
| PB-005 | Configuration management (pydantic-settings) | To Do | |
| PB-006 | Health check endpoint | To Do | |
| PB-007 | Test infrastructure (pytest + pytest-asyncio) | To Do | |
| PB-008 | Ruff linting configuration | To Do | |

**Sprint Goal:** Runnable FastAPI app with DB connectivity, Docker environment, and test infrastructure.

**Definition of Done:** `docker compose up -d` starts PostgreSQL + Redis + API, `GET /health` returns healthy, `pytest` runs with at least one passing test.

---

## Sprint Summary

| Sprint | Epic | Status | Stories |
|--------|------|--------|---------|
| Sprint 1 | Project Foundation & Infrastructure | **Active** | PB-001 to PB-008 |
| Sprint 2 | Tenant Management & Authentication | Planned | PB-009 to PB-015 |
| Sprint 3 | DSR Core | Planned | PB-016 to PB-023 |
| Sprint 4 | DSR Execution, Redis & Audit Logging | Planned | PB-024 to PB-033 |
| Sprint 5 | Consent Management | Planned | PB-034 to PB-040 |
| Sprint 6 | Polish, Documentation & Deployment | Planned | PB-041 to PB-046 |
