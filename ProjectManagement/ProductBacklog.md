# Product Backlog

## Privacy Rights API — GDPR/CCPA Data Subject Request Service

**Product Owner:** Claude (AI)
**Developer:** Bala Kailash
**Methodology:** Agile (Scrum)
**Created:** 2026-02-10

---

## Backlog Items

### Epic 1: Project Foundation & Infrastructure

| ID | Story | Priority | Estimate | Sprint |
|----|-------|----------|----------|--------|
| PB-001 | Project scaffolding (FastAPI app, pyproject.toml, directory structure) | Critical | 2 pts | Sprint 1 |
| PB-002 | Docker Compose setup (PostgreSQL + Redis + API) | Critical | 3 pts | Sprint 1 |
| PB-003 | Async SQLAlchemy + asyncpg database connection setup | Critical | 2 pts | Sprint 1 |
| PB-004 | Alembic migration configuration (async) | Critical | 2 pts | Sprint 1 |
| PB-005 | Configuration management with pydantic-settings | Critical | 1 pt | Sprint 1 |
| PB-006 | Health check endpoint (GET /health) | High | 1 pt | Sprint 1 |
| PB-007 | Pytest + pytest-asyncio test infrastructure with fixtures | High | 2 pts | Sprint 1 |
| PB-008 | Ruff linting and formatting configuration | Medium | 1 pt | Sprint 1 |

### Epic 2: Tenant Management & Authentication

| ID | Story | Priority | Estimate | Sprint |
|----|-------|----------|----------|--------|
| PB-009 | Tenant SQLAlchemy model + Alembic migration | Critical | 2 pts | Sprint 2 |
| PB-010 | APIKey SQLAlchemy model + Alembic migration | Critical | 2 pts | Sprint 2 |
| PB-011 | API key authentication middleware (X-API-Key header, SHA-256 hash lookup) | Critical | 3 pts | Sprint 2 |
| PB-012 | Tenant CRUD endpoints (POST, GET, PATCH /api/v1/tenants) | High | 3 pts | Sprint 2 |
| PB-013 | API key generation on tenant creation (return key once, store hash) | High | 2 pts | Sprint 2 |
| PB-014 | RFC 7807 error response format (global exception handler) | High | 2 pts | Sprint 2 |
| PB-015 | Unit + integration tests for tenant and auth | High | 2 pts | Sprint 2 |

### Epic 3: DSR Core (Submission, Listing, Status Transitions)

| ID | Story | Priority | Estimate | Sprint |
|----|-------|----------|----------|--------|
| PB-016 | DSR SQLAlchemy model + Alembic migration | Critical | 2 pts | Sprint 3 |
| PB-017 | DSRStatusHistory SQLAlchemy model + migration | Critical | 1 pt | Sprint 3 |
| PB-018 | DSR submission endpoint (POST /api/v1/dsr) with SLA deadline computation | Critical | 3 pts | Sprint 3 |
| PB-019 | DSR listing endpoint (GET /api/v1/dsr) with filters and cursor-based pagination | High | 3 pts | Sprint 3 |
| PB-020 | DSR detail endpoint (GET /api/v1/dsr/{id}) with status history | High | 2 pts | Sprint 3 |
| PB-021 | DSR status transition endpoint (PATCH /api/v1/dsr/{id}/status) with state machine validation | Critical | 3 pts | Sprint 3 |
| PB-022 | Parameterized tests for all valid + invalid DSR status transitions | High | 2 pts | Sprint 3 |
| PB-023 | DSR integration tests (submission, listing, detail) | High | 2 pts | Sprint 3 |

### Epic 4: DSR Execution, Redis, & Audit Logging

| ID | Story | Priority | Estimate | Sprint |
|----|-------|----------|----------|--------|
| PB-024 | Redis async connection setup (redis.asyncio) | Critical | 2 pts | Sprint 4 |
| PB-025 | AuditLog SQLAlchemy model + migration | Critical | 2 pts | Sprint 4 |
| PB-026 | Audit logging middleware (auto-log all state-changing operations) | Critical | 3 pts | Sprint 4 |
| PB-027 | DSR execute endpoint (POST /api/v1/dsr/{id}/execute, returns 202) | Critical | 3 pts | Sprint 4 |
| PB-028 | Background task for DSR execution (simulated handlers per request type) | High | 3 pts | Sprint 4 |
| PB-029 | Idempotent DSR execution (re-executing completed DSR returns cached result) | High | 2 pts | Sprint 4 |
| PB-030 | Retry logic for failed DSR executions (max 3 attempts, exponential backoff) | Medium | 2 pts | Sprint 4 |
| PB-031 | DSR statistics endpoint (GET /api/v1/dsr/stats) with Redis caching (5min TTL) | High | 2 pts | Sprint 4 |
| PB-032 | Audit log query endpoint (GET /api/v1/audit) | High | 2 pts | Sprint 4 |
| PB-033 | Tests for execution, audit logging, and stats | High | 2 pts | Sprint 4 |

### Epic 5: Consent Management

| ID | Story | Priority | Estimate | Sprint |
|----|-------|----------|----------|--------|
| PB-034 | ConsentRecord SQLAlchemy model + migration (unique constraint on tenant_id, subject_email, purpose) | Critical | 2 pts | Sprint 5 |
| PB-035 | Consent creation endpoint (POST /api/v1/consent) with 409 on duplicate | High | 2 pts | Sprint 5 |
| PB-036 | Consent listing endpoint (GET /api/v1/consent) with filters + pagination | High | 2 pts | Sprint 5 |
| PB-037 | Consent subject lookup (GET /api/v1/consent/{subject_email}) with Redis caching (15min TTL) | High | 2 pts | Sprint 5 |
| PB-038 | Consent update/withdrawal endpoint (PUT /api/v1/consent/{id}) with cache invalidation | High | 2 pts | Sprint 5 |
| PB-039 | Consent audit trail endpoint (GET /api/v1/consent/audit) | Medium | 2 pts | Sprint 5 |
| PB-040 | Consent integration tests | High | 2 pts | Sprint 5 |

### Epic 6: Polish, Documentation & Deployment

| ID | Story | Priority | Estimate | Sprint |
|----|-------|----------|----------|--------|
| PB-041 | API key tenant lookup Redis caching (30min TTL) with invalidation | Medium | 2 pts | Sprint 6 |
| PB-042 | Rate limiting (100 req/min per API key, configurable) | Medium | 2 pts | Sprint 6 |
| PB-043 | OpenAPI documentation review and cleanup (tags, descriptions, examples) | Medium | 2 pts | Sprint 6 |
| PB-044 | Docker Compose end-to-end verification (single command startup) | High | 2 pts | Sprint 6 |
| PB-045 | README with setup instructions, architecture overview, API examples | Medium | 2 pts | Sprint 6 |
| PB-046 | Final test coverage report (target 80%+) | High | 2 pts | Sprint 6 |

---

## Priority Legend

- **Critical**: Must have — core functionality, system won't work without it
- **High**: Should have — important for compliance and usability
- **Medium**: Nice to have — improves quality and developer experience
