from __future__ import annotations

from fastapi import APIRouter

from ..settings import get_settings

router = APIRouter()


@router.get("/healthz")
async def healthz():
    s = get_settings()
    return {"status": "ok", "env": s.app_env, "app": s.app_name}


@router.get("/info")
async def info():
    s = get_settings()
    return {
        "app": s.app_name,
        "env": s.app_env,
        "temporal": {"target": s.temporal_target, "namespace": s.temporal_namespace},
    }


@router.get("/version")
async def version():
    return {"version": "0.1.0"}

