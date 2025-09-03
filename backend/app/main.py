from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, runs, schemas, events, test_portal
from .artifacts.client import ensure_bucket


app = FastAPI(title="RCM OS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    # Ensure artifact bucket exists (best-effort)
    try:
        ensure_bucket()
    except Exception:
        pass


app.include_router(health.router)
app.include_router(runs.router)
app.include_router(schemas.router)
app.include_router(events.router)
app.include_router(test_portal.router)
