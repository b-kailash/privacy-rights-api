# Privacy Rights API

A FastAPI microservice for managing GDPR/CCPA data subject requests (DSRs), consent records, and audit trails with multi-tenant isolation.

## Features

- **Data Subject Request (DSR) Management** — Full lifecycle from submission through review, approval, execution, and closure
- **Consent Record Management** — Track and audit user consent with full history
- **Multi-Tenant Isolation** — Strict data separation between organizations via API key authentication
- **Audit Trail** — Immutable logging of all state-changing operations
- **SLA Tracking** — 30-day GDPR compliance deadline monitoring
- **Async-First** — Built entirely on async/await for high performance
- **Redis Caching** — Cached consent lookups and DSR statistics

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | FastAPI 0.100+ |
| Language | Python 3.11+ |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 14+ |
| Cache/Queue | Redis 7+ |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio + httpx |
| Containerization | Docker + Docker Compose |

## Project Structure

```
app/
├── api/v1/        # Route handlers (routers)
├── core/          # Config, database, Redis connections
├── middleware/     # Auth, tenant scoping, audit logging
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response schemas
├── services/      # Business logic
└── main.py        # FastAPI application entry point
tests/             # All pytest tests
alembic/           # Database migrations
Docs/              # SRS and specifications
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional, for containerized setup)

### Local Development

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run the API
uvicorn app.main:app --reload
```

### Docker

```bash
docker compose up -d
```

### Verify

- API root: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Development

```bash
# Run tests
pytest

# Run a single test
pytest tests/test_file.py::test_name -v

# Lint
ruff check .

# Format
ruff format .

# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/tenants` | Create a new tenant with API key |
| `POST /api/v1/dsr` | Submit a data subject request |
| `GET /api/v1/dsr` | List DSRs with filters and pagination |
| `PATCH /api/v1/dsr/{id}/status` | Transition DSR status |
| `POST /api/v1/dsr/{id}/execute` | Execute an approved DSR (async) |
| `GET /api/v1/dsr/stats` | DSR statistics |
| `POST /api/v1/consent` | Record consent |
| `GET /api/v1/consent/{email}` | Look up consent by subject |
| `PUT /api/v1/consent/{id}` | Update/withdraw consent |
| `GET /api/v1/audit` | Query audit logs |
| `GET /health` | Health check |

All endpoints require `X-API-Key` header authentication (except `/health` and `/docs`).

## License

Private — All rights reserved.
