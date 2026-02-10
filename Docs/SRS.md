# Software Requirements Specification (SRS)

## Project: Privacy Rights API -- GDPR/CCPA Data Subject Request Service

**Version:** 1.0
**Date:** 2026-02-10
**Author:** Bala Kailash
**Status:** Draft

---

### Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-10 | Initial draft |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for the **Privacy Rights API**, a FastAPI-based microservice that enables organizations to manage data subject requests (DSRs) under GDPR and CCPA regulations, record and audit user consent, and enforce data retention policies. The system is designed to serve multiple tenants (organizations) with strict data isolation.

### 1.2 Scope

The Privacy Rights API provides:
- Multi-tenant data subject request (DSR) lifecycle management (submission, review, approval, execution, completion)
- Consent record management with full audit trail
- GDPR/CCPA compliance enforcement (30-day SLA tracking, data retention policies)
- Asynchronous processing of long-running privacy operations (data export, deletion)
- Redis-backed caching and task queuing
- RESTful API with OpenAPI/Swagger documentation

**Out of Scope:**
- User-facing consent collection UI (this is a backend API only)
- Integration with specific data stores for actual data deletion (simulated via pluggable handlers)
- Payment processing or billing
- Email/notification delivery (webhook-based notification hooks provided)

### 1.3 Definitions and Glossary

| Term | Definition |
|------|------------|
| **DSR** | Data Subject Request -- a formal request from an individual to exercise their privacy rights |
| **GDPR** | General Data Protection Regulation -- EU privacy regulation (effective May 2018) |
| **CCPA** | California Consumer Privacy Act -- California state privacy law |
| **Data Subject** | An individual whose personal data is processed by an organization |
| **Data Controller** | An organization that determines the purposes and means of processing personal data (represented as a Tenant in this system) |
| **Tenant** | An organization using this platform; each tenant's data is fully isolated |
| **Consent** | A freely given, specific, informed, and unambiguous indication of a data subject's agreement to the processing of their personal data |
| **Right of Access** | GDPR Article 15 -- the right to obtain confirmation and a copy of personal data being processed |
| **Right to Erasure** | GDPR Article 17 -- the right to have personal data deleted ("right to be forgotten") |
| **Right to Rectification** | GDPR Article 16 -- the right to have inaccurate personal data corrected |
| **Right to Portability** | GDPR Article 20 -- the right to receive personal data in a structured, machine-readable format |
| **SLA** | Service Level Agreement -- the 30-day deadline for responding to DSRs under GDPR |
| **DPO** | Data Protection Officer -- the person responsible for overseeing privacy compliance |
| **Audit Trail** | A chronological record of all actions taken on a resource |

### 1.4 Assumptions

- Consumers of this API are internal services or admin dashboards, not end-users directly
- Authentication is handled via API keys per tenant (not individual user OAuth)
- The system simulates actual data operations (access, deletion, export) via pluggable handler interfaces; real integrations are out of scope
- PostgreSQL 14+ is available as the primary data store
- Redis 7+ is available for caching and task queuing
- The API runs in a containerized environment (Docker)

### 1.5 Constraints

- All DSR processing must respect the 30-day GDPR deadline (configurable per regulation)
- Tenant data must be strictly isolated -- no cross-tenant data leakage under any circumstances
- All state-changing operations must produce audit log entries
- The system must handle concurrent requests without data corruption (async-safe)
- All timestamps must be stored in UTC
- API responses must follow consistent error format (RFC 7807 Problem Details)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
│                   (FastAPI Application)                       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ DSR Router   │  │ Consent     │  │ Tenant Router        │ │
│  │ /api/v1/dsr  │  │ Router      │  │ /api/v1/tenants      │ │
│  │              │  │ /api/v1/    │  │                      │ │
│  │              │  │ consent     │  │                      │ │
│  └──────┬───────┘  └──────┬──────┘  └──────────┬───────────┘ │
│         │                 │                     │             │
│  ┌──────┴─────────────────┴─────────────────────┴───────────┐ │
│  │                   Middleware Layer                        │ │
│  │  ┌──────────────┐ ┌───────────┐ ┌─────────────────────┐ │ │
│  │  │ Tenant Scope │ │ Auth      │ │ Audit Logger        │ │ │
│  │  │ Middleware   │ │ Middleware│ │ Middleware           │ │ │
│  │  └──────────────┘ └───────────┘ └─────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Service Layer                          │ │
│  │  ┌─────────────────┐  ┌────────────────────────────────┐ │ │
│  │  │ DSR Processor    │  │ Consent Manager               │ │ │
│  │  │ (Business Logic) │  │ (Business Logic)              │ │ │
│  │  └─────────────────┘  └────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
         │                          │
    ┌────┴─────┐              ┌─────┴─────┐
    │PostgreSQL│              │   Redis   │
    │ (Primary │              │ (Cache +  │
    │  Store)  │              │  Queue)   │
    └──────────┘              └───────────┘
```

### 2.2 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Web Framework** | FastAPI 0.100+ | Async-native, auto-generated OpenAPI docs, Pydantic integration |
| **Language** | Python 3.11+ | async/await support, type hints, ecosystem |
| **ORM** | SQLAlchemy 2.0 (async) | Async session support, mature migration tooling |
| **Async DB Driver** | asyncpg | High-performance async PostgreSQL driver |
| **Database** | PostgreSQL 14+ | ACID compliance, JSONB support, robust indexing |
| **Cache/Queue** | Redis 7+ via redis.asyncio | Async caching, background task queue |
| **Migrations** | Alembic | SQLAlchemy-native, supports async |
| **Validation** | Pydantic v2 | FastAPI-native request/response validation |
| **Configuration** | pydantic-settings | Type-safe settings from environment variables |
| **Testing** | pytest + pytest-asyncio | Async test support, fixtures |
| **HTTP Testing** | httpx (AsyncClient) | FastAPI's recommended async test client |
| **Code Quality** | Ruff + Black | Linting and formatting (consistent with NeoZen) |
| **Containerization** | Docker + Docker Compose | PostgreSQL + Redis + API orchestration |

### 2.3 Design Principles

1. **Async-First:** All database queries, Redis operations, and I/O use `async/await`. No blocking calls in request handlers.
2. **Tenant Isolation:** Every database query is scoped by `tenant_id`. A middleware extracts tenant context from the API key and injects it into the request state.
3. **Audit Everything:** All create, update, and delete operations produce immutable audit log entries.
4. **Pluggable Handlers:** Actual data operations (fetching user data, deleting records) are abstracted behind handler interfaces, allowing simulation or real integration.
5. **Idempotent Operations:** DSR execution endpoints are idempotent -- re-executing a completed DSR returns the same result.
6. **Fail-Safe Defaults:** If a DSR approaches its SLA deadline without resolution, the system flags it as `overdue` (does not auto-execute).

---

## 3. Data Model

### 3.1 Entity Relationship Overview

```
Tenant (1) ──── (N) APIKey
Tenant (1) ──── (N) DSR
Tenant (1) ──── (N) ConsentRecord
Tenant (1) ──── (N) AuditLog
DSR    (1) ──── (N) DSRStatusHistory
DSR    (1) ──── (N) AuditLog
ConsentRecord (1) ── (N) AuditLog
```

### 3.2 Tenant

Represents an organization (data controller) using the platform.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique tenant identifier |
| name | VARCHAR(255) | NOT NULL, UNIQUE | Organization name |
| slug | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | URL-safe identifier |
| regulation | ENUM | NOT NULL, DEFAULT 'gdpr' | Primary regulation: `gdpr`, `ccpa`, `lgpd`, `custom` |
| sla_days | INTEGER | NOT NULL, DEFAULT 30 | DSR response deadline in days |
| retention_days | INTEGER | NULLABLE | Default data retention period |
| dpo_email | VARCHAR(255) | NULLABLE | Data Protection Officer contact |
| webhook_url | VARCHAR(500) | NULLABLE | Notification webhook endpoint |
| config | JSONB | DEFAULT '{}' | Tenant-specific configuration |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Active status |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp (UTC) |
| updated_at | TIMESTAMPTZ | NOT NULL, auto-update | Last modification timestamp (UTC) |

### 3.3 APIKey

Authentication credentials for tenant API access.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Key identifier |
| tenant_id | UUID | FK → Tenant.id, NOT NULL, INDEX | Owning tenant |
| key_hash | VARCHAR(255) | NOT NULL, UNIQUE | SHA-256 hash of the API key |
| key_prefix | VARCHAR(8) | NOT NULL | First 8 chars of key (for identification) |
| name | VARCHAR(100) | NOT NULL | Descriptive name (e.g., "Production Key") |
| scopes | JSONB | NOT NULL, DEFAULT '["read","write"]' | Permitted operations |
| expires_at | TIMESTAMPTZ | NULLABLE | Optional expiration |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Active status |
| last_used_at | TIMESTAMPTZ | NULLABLE | Last API call timestamp |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |

### 3.4 DSR (Data Subject Request)

Core entity representing a privacy rights request.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Request identifier |
| tenant_id | UUID | FK → Tenant.id, NOT NULL, INDEX | Owning tenant (isolation) |
| external_id | VARCHAR(255) | NULLABLE, UNIQUE per tenant | Caller-provided reference ID |
| subject_email | VARCHAR(255) | NOT NULL, INDEX | Data subject's email |
| subject_id | VARCHAR(255) | NULLABLE | Data subject's internal ID in tenant's system |
| request_type | ENUM | NOT NULL | `access`, `deletion`, `rectification`, `portability` |
| regulation | ENUM | NOT NULL | `gdpr`, `ccpa`, `lgpd`, `custom` |
| status | ENUM | NOT NULL, DEFAULT 'pending', INDEX | See status lifecycle below |
| priority | ENUM | NOT NULL, DEFAULT 'normal' | `low`, `normal`, `high`, `urgent` |
| description | TEXT | NULLABLE | Additional context from the requestor |
| submitted_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | When the request was submitted |
| sla_deadline | TIMESTAMPTZ | NOT NULL | Computed: submitted_at + tenant.sla_days |
| reviewed_at | TIMESTAMPTZ | NULLABLE | When an operator reviewed the request |
| reviewed_by | VARCHAR(255) | NULLABLE | Operator who reviewed |
| approved_at | TIMESTAMPTZ | NULLABLE | When the request was approved |
| approved_by | VARCHAR(255) | NULLABLE | Operator who approved |
| executed_at | TIMESTAMPTZ | NULLABLE | When execution started |
| completed_at | TIMESTAMPTZ | NULLABLE | When execution finished |
| closed_at | TIMESTAMPTZ | NULLABLE | When the request was formally closed |
| result_data | JSONB | NULLABLE | Execution results (e.g., data export metadata) |
| error_message | TEXT | NULLABLE | Error details if execution failed |
| metadata | JSONB | DEFAULT '{}' | Arbitrary metadata |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Record creation |
| updated_at | TIMESTAMPTZ | NOT NULL, auto-update | Last modification |

**DSR Status Lifecycle:**

```
                    ┌─────────┐
                    │ pending │  (initial state)
                    └────┬────┘
                         │ review
                    ┌────▼──────┐
              ┌─────│ in_review │─────┐
              │     └───────────┘     │
              │ approve               │ reject
         ┌────▼────┐           ┌──────▼──────┐
         │approved │           │  rejected   │
         └────┬────┘           └─────────────┘
              │ execute
         ┌────▼──────┐
         │processing │
         └────┬──────┘
              │
         ┌────▼──┐──────┐
         │       │      │
    ┌────▼──┐ ┌──▼───┐ ┌▼──────┐
    │completed│ │failed│ │cancelled│
    └────┬──┘ └──────┘ └────────┘
         │ close
    ┌────▼──┐
    │closed │  (terminal state)
    └───────┘
```

**Valid Status Values:** `pending`, `in_review`, `approved`, `rejected`, `processing`, `completed`, `failed`, `cancelled`, `closed`

**Valid Status Transitions:**

| From | To | Trigger |
|------|----|---------|
| pending | in_review | Operator begins review |
| pending | cancelled | Request withdrawn |
| in_review | approved | Operator approves |
| in_review | rejected | Operator rejects (with reason) |
| in_review | pending | Returned for more information |
| approved | processing | Execution initiated |
| approved | cancelled | Cancelled before execution |
| processing | completed | Execution succeeded |
| processing | failed | Execution encountered error |
| completed | closed | Formally closed after verification |
| failed | pending | Reset for retry |
| rejected | pending | Re-opened after appeal |

### 3.5 DSRStatusHistory

Immutable log of all status transitions for a DSR.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGINT | PK, auto-increment | Record ID |
| dsr_id | UUID | FK → DSR.id, NOT NULL, INDEX | Parent DSR |
| from_status | ENUM | NULLABLE | Previous status (NULL for initial) |
| to_status | ENUM | NOT NULL | New status |
| changed_by | VARCHAR(255) | NOT NULL | Operator or 'system' |
| reason | TEXT | NULLABLE | Reason for transition (required for reject) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Transition timestamp |

### 3.6 ConsentRecord

Records a data subject's consent for a specific processing purpose.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Record identifier |
| tenant_id | UUID | FK → Tenant.id, NOT NULL, INDEX | Owning tenant |
| subject_email | VARCHAR(255) | NOT NULL, INDEX | Data subject's email |
| subject_id | VARCHAR(255) | NULLABLE | Data subject's internal ID |
| purpose | VARCHAR(255) | NOT NULL | Processing purpose (e.g., "marketing_emails", "analytics") |
| status | ENUM | NOT NULL, DEFAULT 'active' | `active`, `withdrawn`, `expired` |
| legal_basis | ENUM | NOT NULL | `consent`, `contract`, `legal_obligation`, `vital_interest`, `public_task`, `legitimate_interest` |
| granted_at | TIMESTAMPTZ | NOT NULL | When consent was given |
| withdrawn_at | TIMESTAMPTZ | NULLABLE | When consent was withdrawn |
| expires_at | TIMESTAMPTZ | NULLABLE | Auto-expiry date |
| ip_address | VARCHAR(45) | NULLABLE | IP from which consent was given (IPv4/IPv6) |
| user_agent | VARCHAR(500) | NULLABLE | Browser/client that gave consent |
| proof_reference | VARCHAR(500) | NULLABLE | Reference to consent proof (e.g., form submission ID) |
| metadata | JSONB | DEFAULT '{}' | Additional context |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Record creation |
| updated_at | TIMESTAMPTZ | NOT NULL, auto-update | Last modification |

**Unique Constraint:** `(tenant_id, subject_email, purpose)` -- one consent record per subject per purpose per tenant.

### 3.7 AuditLog

Immutable record of all system actions. Never updated or deleted.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGINT | PK, auto-increment | Log entry ID |
| tenant_id | UUID | FK → Tenant.id, NOT NULL, INDEX | Tenant context |
| entity_type | VARCHAR(50) | NOT NULL, INDEX | `dsr`, `consent`, `tenant`, `api_key` |
| entity_id | UUID | NOT NULL, INDEX | ID of the affected entity |
| action | VARCHAR(50) | NOT NULL | `created`, `updated`, `status_changed`, `deleted`, `accessed`, `exported` |
| actor | VARCHAR(255) | NOT NULL | Who performed the action (API key name or 'system') |
| changes | JSONB | NULLABLE | Before/after snapshot of changed fields |
| ip_address | VARCHAR(45) | NULLABLE | Request source IP |
| request_id | UUID | NULLABLE | Correlation ID from request header |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now(), INDEX | Action timestamp |

**Index:** Composite index on `(tenant_id, entity_type, entity_id, created_at)` for efficient audit queries.

---

## 4. API Specification

### 4.1 Authentication

All requests must include an API key in the `X-API-Key` header.

```
X-API-Key: pra_live_a1b2c3d4e5f6...
```

The middleware:
1. Extracts the key from the header
2. Hashes it with SHA-256
3. Looks up the hash in the `api_keys` table
4. Verifies the key is active and not expired
5. Loads the associated tenant into `request.state.tenant`
6. All subsequent queries are automatically scoped to this tenant

**Error Response (401):**
```json
{
  "type": "https://privacy-rights-api.dev/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Invalid or missing API key"
}
```

### 4.2 Error Format

All errors follow RFC 7807 Problem Details:

```json
{
  "type": "https://privacy-rights-api.dev/errors/{error-type}",
  "title": "Human-readable title",
  "status": 400,
  "detail": "Specific error description",
  "instance": "/api/v1/dsr/123"
}
```

### 4.3 Pagination

List endpoints support cursor-based pagination:

```
GET /api/v1/dsr?limit=20&cursor=eyJpZCI6MTAwfQ
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "has_more": true,
    "next_cursor": "eyJpZCI6MTIwfQ"
  }
}
```

### 4.4 Tenant Endpoints

#### POST /api/v1/tenants
Create a new tenant. **Requires admin-scoped API key.**

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "regulation": "gdpr",
  "sla_days": 30,
  "dpo_email": "dpo@acme.com",
  "webhook_url": "https://acme.com/webhooks/privacy"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "regulation": "gdpr",
  "sla_days": 30,
  "dpo_email": "dpo@acme.com",
  "is_active": true,
  "created_at": "2026-02-10T12:00:00Z",
  "api_key": {
    "key": "pra_live_a1b2c3d4e5f6...",
    "name": "Default Key",
    "note": "Store this key securely. It will not be shown again."
  }
}
```

#### GET /api/v1/tenants/{tenant_id}
Get tenant details. Scoped to the authenticated tenant.

#### PATCH /api/v1/tenants/{tenant_id}
Update tenant configuration.

### 4.5 DSR Endpoints

#### POST /api/v1/dsr
Submit a new data subject request.

**Request Body:**
```json
{
  "subject_email": "john.doe@example.com",
  "subject_id": "user_12345",
  "request_type": "access",
  "regulation": "gdpr",
  "priority": "normal",
  "description": "I want a copy of all my personal data",
  "external_id": "TICKET-2026-001",
  "metadata": {
    "source": "customer_portal",
    "verified": true
  }
}
```

**Response (201):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "subject_email": "john.doe@example.com",
  "request_type": "access",
  "status": "pending",
  "priority": "normal",
  "submitted_at": "2026-02-10T12:05:00Z",
  "sla_deadline": "2026-03-12T12:05:00Z",
  "sla_days_remaining": 30
}
```

**Validation Rules:**
- `subject_email`: Required, valid email format
- `request_type`: Required, one of `access`, `deletion`, `rectification`, `portability`
- `regulation`: Required, one of `gdpr`, `ccpa`, `lgpd`, `custom`
- `external_id`: If provided, must be unique within the tenant
- `priority`: Optional, defaults to `normal`

#### GET /api/v1/dsr
List DSRs with filtering and pagination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (comma-separated for multiple) |
| request_type | string | Filter by request type |
| subject_email | string | Filter by data subject email |
| priority | string | Filter by priority |
| overdue | boolean | If true, only return DSRs past their SLA deadline |
| submitted_after | datetime | Filter by submission date |
| submitted_before | datetime | Filter by submission date |
| sort | string | Sort field: `submitted_at`, `sla_deadline`, `priority`, `status` |
| order | string | `asc` or `desc` (default: `desc`) |
| limit | integer | Page size (default: 20, max: 100) |
| cursor | string | Pagination cursor |

**Example:** `GET /api/v1/dsr?status=pending,in_review&overdue=true&sort=sla_deadline&order=asc`

#### GET /api/v1/dsr/{dsr_id}
Get full DSR details including status history.

**Response includes:**
```json
{
  "id": "...",
  "status": "in_review",
  "sla_days_remaining": 22,
  "is_overdue": false,
  "status_history": [
    {
      "from_status": null,
      "to_status": "pending",
      "changed_by": "system",
      "created_at": "2026-02-10T12:05:00Z"
    },
    {
      "from_status": "pending",
      "to_status": "in_review",
      "changed_by": "operator@acme.com",
      "created_at": "2026-02-11T09:30:00Z"
    }
  ]
}
```

#### PATCH /api/v1/dsr/{dsr_id}/status
Transition DSR to a new status.

**Request Body:**
```json
{
  "status": "approved",
  "reason": "Identity verified, request is valid",
  "changed_by": "operator@acme.com"
}
```

**Validation:**
- Status transition must be valid per the state machine (Section 3.4)
- `reason` is required when status is `rejected`
- `changed_by` is required

**Error (422) -- Invalid transition:**
```json
{
  "type": "https://privacy-rights-api.dev/errors/invalid-transition",
  "title": "Invalid Status Transition",
  "status": 422,
  "detail": "Cannot transition from 'pending' to 'completed'. Valid transitions: in_review, cancelled"
}
```

#### POST /api/v1/dsr/{dsr_id}/execute
Execute an approved DSR. Triggers async background processing.

**Preconditions:**
- DSR must be in `approved` status
- Transitions DSR to `processing` immediately
- Background task performs the actual operation

**Response (202 Accepted):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "processing",
  "message": "DSR execution started. Poll GET /api/v1/dsr/{id} for progress."
}
```

**Background Processing by Type:**

| Request Type | Action | Result |
|-------------|--------|--------|
| `access` | Collect all personal data for the subject | `result_data` contains data export summary |
| `deletion` | Delete all personal data for the subject | `result_data` contains deletion confirmation |
| `rectification` | Apply corrections specified in metadata | `result_data` contains updated fields |
| `portability` | Generate machine-readable data export (JSON) | `result_data` contains export file reference |

#### GET /api/v1/dsr/stats
Get DSR statistics for the tenant.

**Response:**
```json
{
  "total": 150,
  "by_status": {
    "pending": 12,
    "in_review": 8,
    "approved": 3,
    "processing": 2,
    "completed": 110,
    "rejected": 10,
    "cancelled": 5
  },
  "by_type": {
    "access": 80,
    "deletion": 45,
    "rectification": 15,
    "portability": 10
  },
  "overdue": 2,
  "avg_resolution_days": 8.5,
  "sla_compliance_rate": 98.7
}
```

### 4.6 Consent Endpoints

#### POST /api/v1/consent
Record a new consent.

**Request Body:**
```json
{
  "subject_email": "john.doe@example.com",
  "subject_id": "user_12345",
  "purpose": "marketing_emails",
  "legal_basis": "consent",
  "granted_at": "2026-02-10T12:00:00Z",
  "expires_at": "2027-02-10T12:00:00Z",
  "ip_address": "192.168.1.100",
  "proof_reference": "form_submission_98765"
}
```

**Response (201):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "subject_email": "john.doe@example.com",
  "purpose": "marketing_emails",
  "status": "active",
  "legal_basis": "consent",
  "granted_at": "2026-02-10T12:00:00Z",
  "expires_at": "2027-02-10T12:00:00Z"
}
```

**Conflict (409):** If an active consent already exists for the same subject + purpose + tenant, return 409 with the existing record.

#### GET /api/v1/consent
List consent records with filtering.

**Query Parameters:** `subject_email`, `purpose`, `status`, `legal_basis`, `limit`, `cursor`

#### GET /api/v1/consent/{subject_email}
Get all consent records for a specific data subject.

**Response:** Array of consent records grouped by purpose, with current status.

**Redis Caching:** This endpoint caches responses in Redis with key `consent:{tenant_id}:{subject_email}`. Cache is invalidated on any consent change for that subject.

#### PUT /api/v1/consent/{consent_id}
Update a consent record (e.g., withdraw consent).

**Request Body (withdrawal):**
```json
{
  "status": "withdrawn",
  "withdrawn_at": "2026-03-15T10:00:00Z"
}
```

**Side Effects:**
- Audit log entry created
- Redis cache invalidated for the subject
- If configured, webhook notification sent to tenant

#### GET /api/v1/consent/audit
Query the consent audit trail.

**Query Parameters:** `subject_email`, `purpose`, `action`, `after`, `before`, `limit`, `cursor`

### 4.7 Audit Log Endpoints

#### GET /api/v1/audit
Query audit logs for the tenant.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| entity_type | string | `dsr`, `consent`, `tenant`, `api_key` |
| entity_id | UUID | Specific entity |
| action | string | `created`, `updated`, `status_changed`, `deleted`, `accessed` |
| actor | string | Filter by actor |
| after | datetime | Start date |
| before | datetime | End date |
| limit | integer | Page size (default: 50, max: 200) |
| cursor | string | Pagination cursor |

### 4.8 Health & Metrics Endpoints

#### GET /health
System health check.

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok"
  },
  "timestamp": "2026-02-10T12:00:00Z"
}
```

#### GET /metrics
Prometheus-compatible metrics endpoint (optional stretch goal).

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Target |
|--------|--------|
| API response time (p95) | < 200ms for reads, < 500ms for writes |
| DSR list query (1000 records) | < 300ms |
| Consent lookup (cached) | < 10ms |
| Background DSR execution | < 60 seconds (simulated) |
| Concurrent API requests | 100+ without degradation |

### 5.2 Security

- All API keys stored as SHA-256 hashes (never plaintext)
- Tenant data isolation enforced at the query layer (every query includes `WHERE tenant_id = :tenant_id`)
- Rate limiting: 100 requests/minute per API key (configurable)
- Input validation on all endpoints via Pydantic
- SQL injection prevention via parameterized queries (SQLAlchemy)
- Sensitive fields (API keys, passwords) never included in API responses or logs
- Audit log entries are append-only (no UPDATE or DELETE)

### 5.3 Reliability

- Database transactions for all multi-step operations
- Idempotent DSR execution (re-executing a completed DSR returns cached result)
- Background tasks retry on failure (max 3 attempts with exponential backoff)
- Health check endpoint for monitoring

### 5.4 Testing

| Test Type | Coverage Target | Tools |
|-----------|----------------|-------|
| Unit tests | 80%+ | pytest, pytest-asyncio |
| API integration tests | All endpoints | httpx AsyncClient |
| Database tests | All models and queries | pytest with test database |
| Status transition tests | All valid and invalid transitions | Parameterized pytest |

### 5.5 Documentation

- Auto-generated OpenAPI/Swagger docs at `/docs`
- ReDoc alternative at `/redoc`
- README with setup instructions, architecture overview, and API examples

---

## 6. Redis Usage

### 6.1 Caching Strategy

| Key Pattern | Data | TTL | Invalidation |
|-------------|------|-----|-------------|
| `consent:{tenant_id}:{subject_email}` | All consent records for a subject | 15 minutes | On any consent change for that subject |
| `dsr:stats:{tenant_id}` | Tenant DSR statistics | 5 minutes | On any DSR status change |
| `tenant:{api_key_hash}` | Tenant lookup from API key | 30 minutes | On API key change |

### 6.2 Background Task Queue

| Queue | Purpose |
|-------|---------|
| `dsr:execute:{tenant_id}` | DSR execution tasks |
| `dsr:notify:{tenant_id}` | Webhook notification tasks |

Tasks are serialized as JSON and processed by background workers using `asyncio.create_task` or a simple Redis-based polling loop.

---

## 7. Development Phases

### Phase 1: Foundation (Days 1-3)
- Project scaffolding (FastAPI, pyproject.toml, Docker Compose)
- Async SQLAlchemy setup with asyncpg
- Alembic migration configuration
- Tenant and APIKey models + migrations
- API key authentication middleware
- Tenant CRUD endpoints
- Health check endpoint
- Basic pytest setup with async fixtures

### Phase 2: DSR Core (Days 4-6)
- DSR model + migration
- DSRStatusHistory model
- DSR submission endpoint (POST)
- DSR listing with filters and pagination
- DSR detail endpoint
- Status transition endpoint with state machine validation
- Status transition tests (all valid + invalid paths)

### Phase 3: DSR Execution + Redis (Days 7-9)
- Redis async connection setup
- Background task for DSR execution (simulated handlers)
- DSR execute endpoint (POST, returns 202)
- DSR statistics endpoint with Redis caching
- Retry logic for failed executions
- Audit log model + middleware

### Phase 4: Consent + Polish (Days 10-12)
- ConsentRecord model + migration
- Consent CRUD endpoints
- Consent subject lookup with Redis caching
- Consent audit trail endpoint
- Cache invalidation on consent changes
- API integration tests for all endpoints

### Phase 5: Documentation + Deployment (Days 13-14)
- README with architecture overview and setup guide
- Verify all async patterns are correct
- Docker Compose works end-to-end (PostgreSQL + Redis + API)
- OpenAPI docs review and cleanup
- Final test run with coverage report

---

## 8. Acceptance Criteria

The project is complete when:

1. All endpoints listed in Section 4 are implemented and return correct responses
2. All DSR status transitions follow the state machine in Section 3.4
3. Tenant data isolation is enforced -- no cross-tenant data access is possible
4. Redis caching works for consent lookups and DSR statistics
5. Background DSR execution works asynchronously
6. Audit log entries are created for all state-changing operations
7. All API responses follow RFC 7807 error format
8. Test coverage is 80%+ with all status transition paths covered
9. Docker Compose starts PostgreSQL + Redis + API with a single command
10. OpenAPI documentation is auto-generated and accurate at `/docs`
