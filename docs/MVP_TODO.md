# MVP TODOs: AI‑Native RCM OS

This document gives every agent full context on the MVP vision and the exact, testable tasks to deliver it. Each item is independently completable and verifiable with clear acceptance criteria and quick test steps.

## Context Overview

- Vision: Build the AI‑native, human‑assisted RCM OS. Automate payer portal workflows with browser agents; use clearinghouse rails where possible; keep humans in the loop for edge cases; emit typed, auditable outputs.
- MVP Scope: Availity eligibility and UnitedHealthcare claim status; ops console for HITL; staff batch uploads; unified APIs; artifacts and metrics.
- Selected Stack:
  - Backend: Python + FastAPI, PostgreSQL, SQLAlchemy 2 + Alembic
  - Orchestration: Temporal (Python SDK `temporalio`)
  - Agents: Playwright (Python), YAML→steps compiler
  - Frontend: Next.js + React + Tailwind (ops console)
  - Events: Redis Pub/Sub (fan‑out) + Redis Streams (durable); upgradable to Kafka
  - Artifacts: S3/MinIO via `boto3` with signed URL access
  - Observability: OpenTelemetry tracing, Prometheus metrics; structured logs
  - Clearinghouse: Stedi for 270/271 (eligibility) and 276/277 (claim status)
  - Security: PHI minimization, TLS, encryption at rest, secrets vaulting, audit logs

## Working Agreements

- Definition of Done: Code + tests + docs; runs locally via `docker-compose`; endpoints verified with `curl` or simple scripts; metrics and logs observable.
- Idempotency Key: `(payer_id, purpose, business_ids..., business_date)`; reject/return existing on duplicates.
- Event Envelope: `{ type, run_id?, batch_id?, payload, ts, source }` on Redis.
- Environments: Local via `docker-compose` for Temporal, Postgres, MinIO, Redis, API, worker, and frontend.
- Security Defaults: Secrets in env or vault, least‑privilege credentials, signed URLs for artifacts, audit all HITL actions.

---

## Task List (Assignable, Testable)

Each task includes Objective, Deliverables, Dependencies, and Verification. Use IDs to assign and track.

### Bootstrap & Infra

T‑001 Repo and Settings Scaffold [Status: completed]
- Objective: Establish FastAPI project layout and settings module.
- Deliverables: `backend/app/main.py`, `backend/app/settings.py`, `pyproject.toml`, `README.md` run instructions.
- Dependencies: None.
- Verification: `uvicorn backend.app.main:app --reload` returns 200 on `GET /healthz`.

T‑002 Docker Compose Stack [Status: completed]
- Objective: Local stack for Postgres, Redis, MinIO, Temporal, API, Worker, Frontend.
- Deliverables: `infra/docker-compose.yml`, `.env.example`, service healthchecks.
- Dependencies: T‑001.
- Verification: `docker compose up -d` then `curl localhost:8000/healthz` 200; Temporal UI accessible; MinIO console accessible.

T‑003 Database Baseline [Status: completed]
- Objective: SQLAlchemy 2 + Alembic setup.
- Deliverables: `backend/app/db.py`, `alembic.ini`, `migrations/` initial revision.
- Dependencies: T‑001, T‑002.
- Verification: `alembic upgrade head`; table creation succeeds; `GET /healthz` DB ping passes.

T‑004 Artifact Storage Wiring [Status: completed]
- Objective: MinIO/S3 client and default bucket creation.
- Deliverables: `backend/app/artifacts/client.py`, bucket name config, signed URL helper.
- Dependencies: T‑002.
- Verification: `POST /test/artifact` writes a file; `GET /runs/{id}/artifacts` returns signed URL opening an image.

### Schemas & Contracts

T‑010 Pydantic Models and JSON Schemas [Status: completed]
- Objective: Define input/output schemas for eligibility and claim status.
- Deliverables: `backend/app/schemas/eligibility.py`, `.../claim_status.py`, JSON Schema export endpoint `GET /schemas`.
- Dependencies: T‑001.
- Verification: JSON Schema validates sample payloads; `pytest` unit tests pass.

T‑011 Idempotency Utility [Status: completed]
- Objective: Deterministic key generator and dedupe table.
- Deliverables: `backend/app/utils/idempotency.py`, `idempotent_runs` table + Alembic migration.
- Dependencies: T‑003.
- Verification: Same input returns existing run id; new input creates new run.

T‑012 Event Envelope + Redis Client [Status: completed]
- Objective: Standard event format and publisher/consumer helpers.
- Deliverables: `backend/app/events/envelope.py`, `.../bus.py` (publish, subscribe, stream group).
- Dependencies: T‑002.
- Verification: Publish/subscribe loopback test; event recorded in Streams with group ack.

### Backend APIs

T‑020 FastAPI Core Endpoints [Status: completed]
- Objective: Health, version, config introspection (non‑sensitive).
- Deliverables: `GET /healthz`, `GET /version`, `GET /info`.
- Dependencies: T‑001.
- Verification: Curl returns expected JSON.

T‑021 Runs API (Start/Status) [Status: completed]
- Objective: Start a run and fetch status.
- Deliverables: `POST /runs`, `GET /runs/{id}`; Pydantic validation; idempotency.
- Dependencies: T‑010, T‑011.
- Verification: Start returns `run_id`; immediate `GET` shows `queued|running`.

T‑022 Artifacts Listing + Signed URLs [Status: completed]
- Objective: List and access artifacts safely.
- Deliverables: `GET /runs/{id}/artifacts` with signed URLs; manifest persisted.
- Dependencies: T‑004, T‑021.
- Verification: Returns list; URLs download assets; 403 for unauthorized roles.

T‑023 Realtime WS/SSE Bridge [Status: completed]
- Objective: Live updates to UI via WS/SSE consuming Redis Pub/Sub.
- Deliverables: `GET /events` (WS/SSE) with filters (`run_id`, `batch_id`).
- Dependencies: T‑012, T‑020.
- Verification: Open connection receives `run.created` broadcast from a test publisher.

### Orchestration (Temporal)

T‑030 Temporal Server + Client Wiring [Status: completed]
- Objective: Connect Python workers/clients to local Temporal.
- Deliverables: `backend/workflows/client.py`, namespace config, task queue names.
- Dependencies: T‑002.
- Verification: Client can `describe_namespace`; smoke test passes.

T‑031 Workflow Skeleton with HITL [Status: completed]
- Objective: Workflow that pauses for MFA via signal and resumes.
- Deliverables: `backend/workflows/portal.py` with `@workflow.signal provide_mfa(code)`, `@workflow.query get_state()`.
- Dependencies: T‑030.
- Verification: Start workflow, signal MFA, workflow completes (mock activity).

T‑032 Activity: YAML Step Runner (Stub) [Status: completed]
- Objective: Activity that accepts a small YAML flow and returns mocked output.
- Deliverables: `backend/activities/runner.py` with interface and logging.
- Dependencies: T‑031.
- Verification: Workflow invokes activity; returns deterministic JSON.

T‑033 Event Emission from Workflows [Status: completed]
- Objective: Emit `run.created`, `breakpoint.mfa.requested`, `run.succeeded/failed` to Redis.
- Deliverables: Hooks in workflow/activities -> `events.bus.publish()`.
- Dependencies: T‑012, T‑031.
- Verification: Events visible over `GET /events` during a run.

### DSL & Agent Runner

T‑040 YAML DSL v0.1 Spec + Validator
- Objective: Define supported ops and schema.
- Deliverables: `backend/dsl/spec.yaml`, `backend/dsl/validator.py`.
- Dependencies: T‑010.
- Verification: Valid/invalid test flows validate accordingly.

T‑041 Executor Mapping to Playwright
- Objective: Map DSL ops to Playwright actions (navigate, input, click, wait, extract, assert, emit, breakpoint).
- Deliverables: `backend/agents/playwright_executor.py`.
- Dependencies: T‑040.
- Verification: Run against a mocked/fake portal page; assertions pass.

T‑042 Artifact Capture
- Objective: Capture screenshots, DOM snapshots, HAR; write manifest.
- Deliverables: Artifact writers in executor; `run_manifest.json` layout.
- Dependencies: T‑004, T‑041.
- Verification: Artifacts visible via `GET /runs/{id}/artifacts` and open via signed URLs.

T‑043 Replay Harness
- Objective: Deterministic dry‑run on saved DOM snapshots.
- Deliverables: `backend/agents/replay.py` + CLI.
- Dependencies: T‑042.
- Verification: Given snapshot + DSL, replay extracts same structured outputs.

### Clearinghouse (Stedi)

T‑050 Stedi Client + Config
- Objective: HTTP client/auth and config for trading partners.
- Deliverables: `backend/clearinghouse/stedi_client.py`, settings, secrets.
- Dependencies: T‑001, T‑002.
- Verification: Mocked call returns 200; health probe endpoint confirms wiring.

T‑051 270/271 Mapping
- Objective: JSON→X12 (270) and X12→JSON (271) mappers.
- Deliverables: `backend/clearinghouse/eligibility_mapper.py`.
- Dependencies: T‑010, T‑050.
- Verification: Round‑trip tests on sample 270/271 fixtures.

T‑052 276/277 Mapping
- Objective: JSON→X12 (276) and X12→JSON (277) mappers.
- Deliverables: `backend/clearinghouse/claim_status_mapper.py`.
- Dependencies: T‑010, T‑050.
- Verification: Round‑trip tests on sample 276/277 fixtures.

T‑053 Stedi Webhook Intake
- Objective: Receive 271/277, attach to runs, update state.
- Deliverables: `POST /webhooks/stedi`, signature verification, event emission.
- Dependencies: T‑021, T‑051, T‑052.
- Verification: POST sample webhook -> run status updates; event visible on `/events`.

T‑054 Control Numbers Persistence
- Objective: ISA/GS control number store per partner.
- Deliverables: `control_numbers` table + DAL; monotonic counters.
- Dependencies: T‑003, T‑050.
- Verification: Concurrent increments remain monotonic; unit tests pass.

### Batch Uploads

T‑060 Batch Tables
- Objective: Persist batches and items with statuses.
- Deliverables: `batches`, `batch_items` tables + Alembic migration.
- Dependencies: T‑003.
- Verification: CRUD smoke tests via SQL.

T‑061 Upload API + Streaming Validation
- Objective: Accept CSV/NDJSON, validate rows, store items.
- Deliverables: `POST /batches`, header mapping, error report storage.
- Dependencies: T‑060, T‑010.
- Verification: Upload sample file; `GET /batches/{id}` shows counts; `GET /batches/{id}/errors` returns report.

T‑062 Batch Executor
- Objective: Throttled enqueuer to start a workflow per valid row; emits events.
- Deliverables: Worker that dequeues `batch_items` -> `POST /runs`/Temporal client.
- Dependencies: T‑021, T‑030, T‑060.
- Verification: Items move to running/succeeded/failed; events stream updates.

T‑063 Results Export
- Objective: Consolidated CSV/JSON export of outputs with artifact links.
- Deliverables: `GET /batches/{id}/results` with signed downloads.
- Dependencies: T‑022, T‑060.
- Verification: Download opens, contains expected fields and URLs.

### HITL Backend

T‑070 Breakpoints Model & API
- Objective: Persist HITL tasks with SLA and audit.
- Deliverables: `breakpoints` table; `GET /inbox`, `POST /inbox/{id}/resolve`.
- Dependencies: T‑003, T‑012, T‑031.
- Verification: Creating a breakpoint surfaces in inbox; resolving signals event.

T‑071 MFA Signal Endpoint
- Objective: Provide MFA code to workflow.
- Deliverables: `POST /runs/{id}/mfa` -> Temporal signal; audit log.
- Dependencies: T‑021, T‑031.
- Verification: Signal unblocks waiting workflow; status becomes running/succeeded.

T‑072 QA Sampling Hooks
- Objective: Sample resolved tasks for secondary review; metrics.
- Deliverables: Sampling policy, `qa_reviews` table, metrics emission.
- Dependencies: T‑070.
- Verification: Sample size matches policy; QA items visible via API.

### Frontend (Ops Console)

T‑080 Next.js Scaffold + Auth
- Objective: Protected app shell with auth.
- Deliverables: `frontend/` app, Tailwind, auth provider, protected routes.
- Dependencies: T‑020.
- Verification: Login redirects work; authorized pages load.

T‑081 Inbox Page
- Objective: Live list of breakpoints with filters and resolve actions.
- Deliverables: `pages/inbox`, WS/SSE subscription; resolve forms.
- Dependencies: T‑070, T‑023.
- Verification: New breakpoint appears in real time; resolve updates state.

T‑082 Run Detail Page
- Objective: Timeline, structured output, artifact viewer, rerun.
- Deliverables: `pages/runs/[id]`, signed URL rendering, JSON viewer.
- Dependencies: T‑022, T‑023.
- Verification: Page shows steps and opens artifacts.

T‑083 Batch Upload + Detail Pages
- Objective: Upload CSV/NDJSON; see progress; export results.
- Deliverables: `pages/batches/new`, `pages/batches/[id]` with progress and downloads.
- Dependencies: T‑061, T‑062, T‑063.
- Verification: Upload -> items queued -> progress updates -> results export works.

T‑084 Metrics Dashboard (Basic)
- Objective: Coverage, success rate, p95, failure taxonomy (by payer/flow).
- Deliverables: `pages/metrics` with backend aggregation endpoint.
- Dependencies: T‑012, T‑090, T‑091.
- Verification: Charts render; numbers align with sample runs.

### Observability & Security

T‑090 OpenTelemetry Tracing
- Objective: Trace FastAPI requests and worker activities.
- Deliverables: OTel SDK setup; spans include `run_id`, `payer`, `flow`.
- Dependencies: T‑020, T‑032.
- Verification: Traces visible in console/exporter; span attributes present.

T‑091 Prometheus Metrics
- Objective: Counters/histograms for success, latency, failures.
- Deliverables: `/metrics` endpoint; worker metrics exporter.
- Dependencies: T‑020.
- Verification: `curl /metrics` exposes expected series; alerts can be defined later.

T‑092 Audit Logging
- Objective: Immutable audit for runs, HITL actions, webhooks.
- Deliverables: `audit_logs` table; append‑only writer; API to query.
- Dependencies: T‑003, T‑021, T‑070.
- Verification: Actions produce audit records; tamper tests fail as expected.

T‑093 Secrets & Credentials Stubs
- Objective: Centralized secrets access and rotation hooks.
- Deliverables: Secrets module (env/KMS), payer credential model.
- Dependencies: T‑001.
- Verification: Secrets injected at runtime; rotation placeholder callable.

### Testing & CI

T‑100 Unit Tests: DSL, Schemas, Idempotency
- Objective: High‑value unit coverage.
- Deliverables: `tests/` covering DSL validator, schema round‑trips, key generator.
- Dependencies: T‑010, T‑040, T‑011.
- Verification: `pytest -q` green.

T‑101 Integration: Workflow with Mocks
- Objective: Temporal workflow runs with mocked runner and Redis.
- Deliverables: Test harness spinning Temporal client + fake bus.
- Dependencies: T‑031, T‑032, T‑012.
- Verification: Workflow completes; events emitted; assertions pass.

T‑102 E2E: Fake Portal Flow
- Objective: Run DSL against a local fake portal to extract fields.
- Deliverables: Simple fake portal app + Playwright run in CI.
- Dependencies: T‑041, T‑042.
- Verification: CI executes headless browser; assertions succeed.

T‑103 CI Pipeline
- Objective: Lint, type‑check, test, build images.
- Deliverables: GitHub Actions (or equivalent) workflows.
- Dependencies: T‑100, T‑101, T‑102.
- Verification: CI passes on PR; images pushed to local registry (if configured).

### Pilot Configuration

T‑110 Payer Configs (Availity + UHC)
- Objective: Configs for portal and clearinghouse routing.
- Deliverables: `config/payers/*.yaml` with capabilities and selectors.
- Dependencies: T‑040, T‑050.
- Verification: Routing chooses Stedi first; falls back to portal per flags.

T‑111 Feature Flags & Routing Policy
- Objective: Toggle clearinghouse vs portal per payer/flow.
- Deliverables: Simple feature flag store; policy evaluator.
- Dependencies: T‑021, T‑050.
- Verification: Toggling changes actual route; events reflect `source`.

---

## Hand‑Off Notes for Agents

- Always update `README.md` with run/test steps when completing a task.
- Emit events for significant state changes; attach `run_id`/`batch_id` consistently.
- Keep outputs strictly conformant to Pydantic/JSON Schemas; version if breaking.
- Prefer robust Playwright locators (`get_by_role`, labels); fall back conservatively.
- Treat CAPTCHA automation as HITL by default unless explicitly permitted by payer and policy.

## Validation Checklist (MVP Exit)

- ≥70% automation on MVP flows; p95 < 3 minutes; HITL touch rate <10%.
- Batch uploads: validate → run → export works at 5k rows without failures.
- Artifacts: screenshots/DOM/HAR present for all portal runs; signed URLs secure.
- Realtime: Inbox and runs update live via WS/SSE; events well‑formed.
- Clearinghouse: 270/271 and 276/277 round‑trip on fixtures; webhook updates runs.
- Security: AuthN/Z in place; audit logs for runs and HITL actions; secrets not logged.
