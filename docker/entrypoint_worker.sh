#!/usr/bin/env bash
set -euo pipefail

echo "[worker] Waiting for database..."
python - <<'PY'
import os, time, sys
from sqlalchemy import create_engine, text
url = os.environ.get('DATABASE_URL')
engine = create_engine(url)
for i in range(60):
    try:
        with engine.connect() as c:
            c.execute(text('select 1'))
            print('[worker] DB ready')
            sys.exit(0)
    except Exception as e:
        print('[worker] DB not ready, retrying...', e)
        time.sleep(1)
print('[worker] DB not ready after timeout')
sys.exit(1)
PY

echo "[worker] Starting Temporal worker..."
exec python -m backend.workers.runner
