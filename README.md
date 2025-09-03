# RCM OS MVP

AI-native, human-assisted Revenue Cycle Management OS. This repo contains the MVP backend (FastAPI + Temporal + Playwright), event plumbing (Redis), artifact storage (MinIO/S3), and a starter ops console.

## Quick Start (Local)

1. Prereqs: Docker, Docker Compose, Python 3.11
2. Copy `.env.example` to `.env` and adjust as needed
3. Start stack: `docker compose up -d`
4. DB migrations run automatically on API start; check logs if needed.
5. Health check: `curl http://localhost:8000/healthz`

Services:
- API: http://localhost:8000
- Temporal UI: http://localhost:8088
- MinIO Console: http://localhost:9001

## Temporal Test Endpoints

Use these to verify the worker + workflow end-to-end:

- Start workflow:
  - `curl -X POST http://localhost:8000/test/portal/run -H 'content-type: application/json' -d '{"flow_id":"test-flow","workflow_id":"wf-test-13","steps":[{"op":"noop"}]}'`
- Check state:
  - `curl http://localhost:8000/test/portal/wf-test-13/state`
- Provide MFA (resume):
  - `curl -X POST http://localhost:8000/test/portal/wf-test-13/mfa -H 'content-type: application/json' -d '{"code":"123456"}'`
- Get result:
  - `curl http://localhost:8000/test/portal/wf-test-13/result`

## Dev (without Docker)

1. Install Poetry; then `poetry install`
2. Run API: `poetry run uvicorn backend.app.main:app --reload`

## Notes

- See `docs/MVP_TODO.md` for the detailed task plan and verification steps.
