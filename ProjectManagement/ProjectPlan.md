# Project Plan

## Privacy Rights API — Sprint Plan

**Product Owner:** Claude (AI)
**Developer:** Bala Kailash
**Sprint Duration:** ~2-3 days each (aligns with SRS phases)

---

## Sprint 1: Project Foundation & Infrastructure
**Goal:** Runnable FastAPI application with database connectivity, Docker environment, and test infrastructure.

### Stories

#### PB-001: Project scaffolding
**As a** developer, **I want** a properly structured FastAPI project with dependency management, **so that** I can start building features on a solid foundation.

**Acceptance Criteria:**
- Directory structure: `app/`, `app/api/`, `app/models/`, `app/services/`, `app/middleware/`, `app/schemas/`, `app/core/`, `tests/`
- `pyproject.toml` with all dependencies (FastAPI, SQLAlchemy, asyncpg, redis, alembic, pydantic-settings, uvicorn, pytest, pytest-asyncio, httpx, ruff)
- `app/main.py` creates the FastAPI application
- App starts with `uvicorn app.main:app --reload`

#### PB-002: Docker Compose setup
**As a** developer, **I want** a Docker Compose configuration, **so that** PostgreSQL, Redis, and the API can run with a single command.

**Acceptance Criteria:**
- `docker-compose.yml` with `postgres`, `redis`, and `api` services
- `Dockerfile` for the API service
- `.env.example` with all required environment variables
- `docker compose up -d` starts all services
- API connects to PostgreSQL and Redis

#### PB-003: Async SQLAlchemy + asyncpg database connection
**As a** developer, **I want** an async database connection pool, **so that** all DB operations are non-blocking.

**Acceptance Criteria:**
- `app/core/database.py` with async engine, async session factory, and `get_db` dependency
- Uses `create_async_engine` with asyncpg
- Connection string from environment variables
- Session is properly closed after each request

#### PB-004: Alembic migration configuration
**As a** developer, **I want** Alembic configured for async migrations, **so that** I can manage database schema changes.

**Acceptance Criteria:**
- `alembic.ini` and `alembic/env.py` configured for async
- `alembic upgrade head` works against the Docker PostgreSQL
- `alembic revision --autogenerate -m "..."` detects model changes

#### PB-005: Configuration management
**As a** developer, **I want** type-safe configuration from environment variables, **so that** settings are validated at startup.

**Acceptance Criteria:**
- `app/core/config.py` using pydantic-settings `BaseSettings`
- Settings: DATABASE_URL, REDIS_URL, API_TITLE, DEBUG, LOG_LEVEL
- `.env` file support for local development

#### PB-006: Health check endpoint
**As an** operator, **I want** a health check endpoint, **so that** I can monitor the API's status.

**Acceptance Criteria:**
- `GET /health` returns `{"status": "healthy", "version": "1.0.0", "checks": {"database": "ok", "redis": "ok"}, "timestamp": "..."}`
- Returns 503 if database or Redis is unreachable
- No authentication required

#### PB-007: Test infrastructure
**As a** developer, **I want** pytest configured with async support and test database fixtures, **so that** I can write tests from the start.

**Acceptance Criteria:**
- `conftest.py` with async fixtures: test database session, test client (httpx AsyncClient)
- Test database created/dropped per test session
- Tests run with `pytest`
- At least one passing smoke test

#### PB-008: Ruff configuration
**As a** developer, **I want** linting and formatting configured, **so that** code quality is consistent.

**Acceptance Criteria:**
- Ruff config in `pyproject.toml` (rules, line length, target Python version)
- `ruff check .` and `ruff format .` work
- No lint errors on initial codebase

**Sprint 1 Definition of Done:** `docker compose up -d` starts PostgreSQL + Redis + API, `GET /health` returns healthy, `pytest` runs with at least one passing test.

---

## Sprint 2: Tenant Management & Authentication
**Goal:** Tenants can be created with API keys. All subsequent endpoints are authenticated and tenant-scoped.

### Stories

#### PB-009: Tenant model + migration
**As a** developer, **I want** the Tenant database model, **so that** I can store organization data.

**Acceptance Criteria:**
- SQLAlchemy model matching SRS Section 3.2 exactly (all fields, types, constraints)
- UUID primary key, TIMESTAMPTZ columns, JSONB config field
- `regulation` as PostgreSQL ENUM: `gdpr`, `ccpa`, `lgpd`, `custom`
- Alembic migration created and applies cleanly

#### PB-010: APIKey model + migration
**As a** developer, **I want** the APIKey database model, **so that** I can store authentication credentials.

**Acceptance Criteria:**
- SQLAlchemy model matching SRS Section 3.3 (all fields)
- Foreign key to Tenant with cascade delete
- `key_hash` is unique, `key_prefix` stores first 8 chars
- JSONB `scopes` field with default `["read", "write"]`

#### PB-011: API key authentication middleware
**As an** API consumer, **I want** requests authenticated via `X-API-Key` header, **so that** only authorized tenants can access the API.

**Acceptance Criteria:**
- Middleware extracts key from `X-API-Key` header
- Hashes with SHA-256, looks up in `api_keys` table
- Verifies key is active and not expired
- Sets `request.state.tenant` with the loaded tenant
- Returns RFC 7807 401 error for invalid/missing keys
- `/health` and `/docs` excluded from auth

#### PB-012: Tenant CRUD endpoints
**As an** admin, **I want** to create and manage tenants via the API.

**Acceptance Criteria:**
- `POST /api/v1/tenants` — creates tenant + default API key, returns tenant data + plaintext key (shown once)
- `GET /api/v1/tenants/{tenant_id}` — returns tenant details (scoped to authenticated tenant)
- `PATCH /api/v1/tenants/{tenant_id}` — updates tenant config
- Pydantic request/response schemas with validation

#### PB-013: API key generation
**As a** system, **I want** to generate secure API keys on tenant creation, **so that** tenants can authenticate.

**Acceptance Criteria:**
- Key format: `pra_live_` + 32 random hex chars
- Store SHA-256 hash + first 8 chars as prefix
- Return plaintext key only in the creation response
- Key is never stored or logged in plaintext

#### PB-014: RFC 7807 error responses
**As an** API consumer, **I want** consistent error responses, **so that** I can handle errors programmatically.

**Acceptance Criteria:**
- Global exception handler returns RFC 7807 format: `type`, `title`, `status`, `detail`, `instance`
- Pydantic validation errors mapped to 422 with details
- 404, 401, 403, 409 all use this format

#### PB-015: Tenant & auth tests
**Acceptance Criteria:**
- Test tenant creation returns API key
- Test authenticated request succeeds
- Test unauthenticated request returns 401
- Test expired/inactive key returns 401
- Test tenant scoping (can't access other tenant's data)

**Sprint 2 Definition of Done:** Tenant creation returns API key, subsequent requests authenticate via `X-API-Key`, tenant isolation is enforced, all errors follow RFC 7807.

---

## Sprint 3: DSR Core
**Goal:** Full DSR lifecycle: submission, listing, detail view, and status transitions with state machine enforcement.

### Stories

#### PB-016: DSR model + migration
**Acceptance Criteria:**
- SQLAlchemy model matching SRS Section 3.4 (all fields, types, constraints)
- `request_type` ENUM: `access`, `deletion`, `rectification`, `portability`
- `status` ENUM: `pending`, `in_review`, `approved`, `rejected`, `processing`, `completed`, `failed`, `cancelled`, `closed`
- `priority` ENUM: `low`, `normal`, `high`, `urgent`
- `external_id` unique per tenant (not globally)
- Foreign key to Tenant, indexed on `tenant_id` and `status`

#### PB-017: DSRStatusHistory model + migration
**Acceptance Criteria:**
- Model matching SRS Section 3.5
- BIGINT auto-increment PK, FK to DSR
- Records `from_status`, `to_status`, `changed_by`, `reason`, `created_at`

#### PB-018: DSR submission endpoint
**Acceptance Criteria:**
- `POST /api/v1/dsr` creates a DSR in `pending` status
- Auto-computes `sla_deadline` = `submitted_at` + tenant's `sla_days`
- Creates initial DSRStatusHistory entry (from_status=NULL, to_status=pending, changed_by=system)
- Validates: `subject_email` (valid email), `request_type`, `regulation`
- If `external_id` provided, enforces uniqueness within tenant
- Returns 201 with DSR data including `sla_days_remaining`

#### PB-019: DSR listing endpoint
**Acceptance Criteria:**
- `GET /api/v1/dsr` returns paginated DSR list scoped to tenant
- Filters: `status` (comma-separated), `request_type`, `subject_email`, `priority`, `overdue`, `submitted_after`, `submitted_before`
- Sort: `submitted_at`, `sla_deadline`, `priority`, `status` with `asc`/`desc`
- Cursor-based pagination with `limit` (default 20, max 100) and `cursor`
- Response: `{"data": [...], "pagination": {"total", "limit", "has_more", "next_cursor"}}`

#### PB-020: DSR detail endpoint
**Acceptance Criteria:**
- `GET /api/v1/dsr/{dsr_id}` returns full DSR with computed `sla_days_remaining`, `is_overdue`
- Includes `status_history` array ordered by `created_at`
- Returns 404 if DSR not found or belongs to different tenant

#### PB-021: DSR status transition endpoint
**Acceptance Criteria:**
- `PATCH /api/v1/dsr/{dsr_id}/status` transitions to new status
- Request body: `status`, `reason` (required for reject), `changed_by` (required)
- Validates transition against state machine (SRS Section 3.4)
- Creates DSRStatusHistory entry
- Updates relevant timestamp fields (`reviewed_at`, `approved_at`, etc.)
- Returns 422 with valid transitions listed if transition is invalid

#### PB-022: Status transition tests
**Acceptance Criteria:**
- Parameterized tests covering all 12 valid transitions
- Parameterized tests covering invalid transitions (e.g., pending→completed)
- Test that `reason` is required for rejection
- Test that `changed_by` is required

#### PB-023: DSR integration tests
**Acceptance Criteria:**
- Full lifecycle test: create → review → approve → (ready for execution)
- Test listing with each filter type
- Test pagination
- Test 404 for non-existent/other-tenant DSR

**Sprint 3 Definition of Done:** DSRs can be submitted, listed, viewed, and transitioned through the full state machine. All transitions are tested.

---

## Sprint 4: DSR Execution, Redis & Audit Logging
**Goal:** Async DSR execution with background tasks, Redis caching for stats, and audit trail on all mutations.

### Stories

#### PB-024: Redis async connection
**Acceptance Criteria:**
- `app/core/redis.py` with `redis.asyncio` connection
- Redis URL from config
- `get_redis` dependency for injection
- Connection pool with proper cleanup on shutdown

#### PB-025: AuditLog model + migration
**Acceptance Criteria:**
- Model matching SRS Section 3.7
- Composite index on `(tenant_id, entity_type, entity_id, created_at)`
- BIGINT auto-increment PK

#### PB-026: Audit logging middleware
**Acceptance Criteria:**
- Automatically creates audit log entries for all POST, PATCH, PUT, DELETE responses
- Captures `tenant_id`, `entity_type`, `entity_id`, `action`, `actor`, `changes`, `ip_address`
- Entries are append-only (no update/delete operations on audit_log table)

#### PB-027: DSR execute endpoint
**Acceptance Criteria:**
- `POST /api/v1/dsr/{dsr_id}/execute` — DSR must be in `approved` status
- Transitions to `processing` immediately, returns 202
- Spawns background task for actual execution
- Returns error if DSR is not in `approved` status

#### PB-028: Background DSR execution handlers
**Acceptance Criteria:**
- Simulated handlers for each request type: `access`, `deletion`, `rectification`, `portability`
- On success: transitions to `completed`, populates `result_data`
- On failure: transitions to `failed`, populates `error_message`
- Pluggable handler interface for future real integrations

#### PB-029: Idempotent execution
**Acceptance Criteria:**
- Re-executing a `completed` DSR returns the cached result without re-processing
- Re-executing a `processing` DSR returns current status

#### PB-030: Retry logic
**Acceptance Criteria:**
- Failed executions retry up to 3 times with exponential backoff
- After max retries, DSR stays in `failed` status

#### PB-031: DSR statistics endpoint
**Acceptance Criteria:**
- `GET /api/v1/dsr/stats` returns counts by status, by type, overdue count, avg resolution days, SLA compliance rate
- Response cached in Redis (`dsr:stats:{tenant_id}`, 5min TTL)
- Cache invalidated on any DSR status change for the tenant

#### PB-032: Audit log query endpoint
**Acceptance Criteria:**
- `GET /api/v1/audit` with filters: `entity_type`, `entity_id`, `action`, `actor`, `after`, `before`
- Cursor-based pagination (default limit 50, max 200)

#### PB-033: Execution & audit tests
**Acceptance Criteria:**
- Test full execution flow: approved → processing → completed
- Test idempotent re-execution
- Test audit log creation on DSR operations
- Test stats endpoint returns correct aggregations

**Sprint 4 Definition of Done:** DSRs can be executed asynchronously, stats are cached in Redis, all mutations produce audit log entries.

---

## Sprint 5: Consent Management
**Goal:** Full consent lifecycle: creation, listing, subject lookup with caching, withdrawal, and audit trail.

### Stories

#### PB-034: ConsentRecord model + migration
**Acceptance Criteria:**
- Model matching SRS Section 3.6
- Unique constraint: `(tenant_id, subject_email, purpose)`
- `status` ENUM: `active`, `withdrawn`, `expired`
- `legal_basis` ENUM: `consent`, `contract`, `legal_obligation`, `vital_interest`, `public_task`, `legitimate_interest`

#### PB-035: Consent creation endpoint
**Acceptance Criteria:**
- `POST /api/v1/consent` creates a consent record with `status=active`
- Returns 409 Conflict if active consent exists for same (tenant, subject_email, purpose)
- Pydantic validation on all fields
- Returns 201 with consent record

#### PB-036: Consent listing endpoint
**Acceptance Criteria:**
- `GET /api/v1/consent` with filters: `subject_email`, `purpose`, `status`, `legal_basis`
- Cursor-based pagination

#### PB-037: Consent subject lookup with caching
**Acceptance Criteria:**
- `GET /api/v1/consent/{subject_email}` returns all consents for the subject
- Redis cached: `consent:{tenant_id}:{subject_email}`, 15min TTL
- Cache miss → DB query → cache result

#### PB-038: Consent update/withdrawal
**Acceptance Criteria:**
- `PUT /api/v1/consent/{consent_id}` supports status change to `withdrawn`
- Sets `withdrawn_at` timestamp
- Invalidates Redis cache for the subject
- Creates audit log entry

#### PB-039: Consent audit trail
**Acceptance Criteria:**
- `GET /api/v1/consent/audit` with filters: `subject_email`, `purpose`, `action`, `after`, `before`
- Cursor-based pagination

#### PB-040: Consent tests
**Acceptance Criteria:**
- Test consent creation and 409 on duplicate
- Test withdrawal and cache invalidation
- Test subject lookup returns from cache on second call
- Test consent audit trail

**Sprint 5 Definition of Done:** Consent records can be created, listed, looked up (with Redis caching), withdrawn, and audited.

---

## Sprint 6: Polish, Documentation & Deployment
**Goal:** Production readiness — rate limiting, caching optimization, documentation, Docker verification, test coverage.

### Stories

#### PB-041: API key tenant lookup caching
**Acceptance Criteria:**
- Cache tenant lookup from API key in Redis (`tenant:{api_key_hash}`, 30min TTL)
- Invalidate on API key deactivation or tenant change
- Reduces DB hits on every authenticated request

#### PB-042: Rate limiting
**Acceptance Criteria:**
- 100 requests/minute per API key (configurable per tenant)
- Returns 429 Too Many Requests with `Retry-After` header
- Rate limit state stored in Redis

#### PB-043: OpenAPI documentation cleanup
**Acceptance Criteria:**
- All endpoints have tags, descriptions, and example request/responses
- `/docs` (Swagger) and `/redoc` render correctly
- Auth scheme documented in OpenAPI spec

#### PB-044: Docker Compose end-to-end verification
**Acceptance Criteria:**
- `docker compose up -d` starts all services from clean state
- Migrations run automatically on API startup
- Health check passes within 30 seconds
- All integration tests pass against Docker services

#### PB-045: README
**Acceptance Criteria:**
- Setup instructions (Docker, local dev)
- Architecture overview
- API usage examples with curl
- Configuration reference

#### PB-046: Final test coverage
**Acceptance Criteria:**
- `pytest --cov` reports 80%+ coverage
- All DSR status transitions tested
- All endpoints tested (happy path + error cases)
- Tenant isolation tested

**Sprint 6 Definition of Done:** `docker compose up -d` runs the full stack, 80%+ test coverage, OpenAPI docs are clean, README is complete.
