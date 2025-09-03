#!/usr/bin/env bash
set -euo pipefail

echo "[api] Waiting for database..."
python - <<'PY'
import os, time, sys
from sqlalchemy import create_engine, text
url = os.environ.get('DATABASE_URL')
engine = create_engine(url)
for i in range(60):
    try:
        with engine.connect() as c:
            c.execute(text('select 1'))
            print('[api] DB ready')
            sys.exit(0)
    except Exception as e:
        print('[api] DB not ready, retrying...', e)
        time.sleep(1)
print('[api] DB not ready after timeout')
sys.exit(1)
PY

echo "[api] Running migrations..."
alembic upgrade head

echo "[api] Starting API server..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
