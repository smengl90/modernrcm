from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..db import session_scope
from ..models import IdempotentRun, Run, RunStatus
from ..schemas.base import RunCreate, RunOut
from ..utils.idempotency import idempotency_key
from ..events.bus import get_bus
from ..events.envelope import Event
from ..artifacts.client import list_prefix, presign_get


router = APIRouter()


@router.post("/runs", response_model=RunOut)
async def create_run(body: RunCreate):
    # Build idempotency key from hints + inputs
    hints = body.idempotency_hints or {}
    business = {k: body.input.get(k) for k in sorted(body.input.keys())}
    key = idempotency_key(body.purpose, body.payer_id, body.provider_npi, {**business, **hints})

    async with session_scope() as s:
        # Dedupe
        existing = await s.get(IdempotentRun, key)
        if existing:
            run = await s.get(Run, existing.run_id)
            assert run
            return RunOut(
                id=str(run.id),
                purpose=run.purpose,
                payer_id=run.payer_id,
                provider_npi=run.provider_npi,
                status=run.status.value,
                source=run.source,
                input=run.input_payload,
                output=run.output_payload,
                error_code=run.error_code,
                error_msg=run.error_msg,
            )

        # Create new run
        run = Run(
            purpose=body.purpose,
            payer_id=body.payer_id,
            provider_npi=body.provider_npi,
            status=RunStatus.queued,
            input_payload=body.input,
        )
        s.add(run)
        await s.flush()

        s.add(IdempotentRun(key=key, run_id=run.id))

        # Emit event
        await get_bus().publish(Event(type="run.created", run_id=str(run.id), payload={"purpose": run.purpose}).dict())

        return RunOut(
            id=str(run.id),
            purpose=run.purpose,
            payer_id=run.payer_id,
            provider_npi=run.provider_npi,
            status=run.status.value,
            source=run.source,
            input=run.input_payload,
            output=run.output_payload,
            error_code=run.error_code,
            error_msg=run.error_msg,
        )


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(run_id: uuid.UUID):
    async with session_scope() as s:
        run = await s.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        return RunOut(
            id=str(run.id),
            purpose=run.purpose,
            payer_id=run.payer_id,
            provider_npi=run.provider_npi,
            status=run.status.value,
            source=run.source,
            input=run.input_payload,
            output=run.output_payload,
            error_code=run.error_code,
            error_msg=run.error_msg,
        )


@router.get("/runs/{run_id}/artifacts")
async def list_artifacts(run_id: uuid.UUID):
    prefix = f"runs/{run_id}/"
    keys = list_prefix(prefix)
    return {"artifacts": [{"key": k, "url": presign_get(k)} for k in keys]}
