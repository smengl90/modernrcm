from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from fastapi import APIRouter, HTTPException

from ...workflows.client import get_temporal_client
from ...workflows.portal import PortalFlow
from ...app.settings import get_settings
import asyncio
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.common import WorkflowIDReusePolicy


router = APIRouter(prefix="/test/portal", tags=["test-portal"])


@router.post("/run")
async def start_portal_flow(body: dict[str, Any] | None = None):
    s = get_settings()
    body = body or {}
    flow_id: str = body.get("flow_id", "test-flow")
    steps: list[dict] = body.get("steps") or [{"op": "noop"}]
    workflow_id: str = body.get("workflow_id", "wf-test-1")

    client = await get_temporal_client()
    try:
        handle = await client.start_workflow(
            PortalFlow.run,
            id=workflow_id,
            task_queue=s.temporal_task_queue,
            args=[flow_id, steps],
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
        )
    except WorkflowAlreadyStartedError:
        handle = client.get_workflow_handle(workflow_id)

    # Best-effort state query (may race with start)
    state_dict: dict[str, Any] = {}
    try:
        state = await handle.query(PortalFlow.get_state)
        state_dict = asdict(state) if is_dataclass(state) else dict(state)
    except Exception:
        pass

    return {"workflow_id": handle.id, "state": state_dict}


@router.get("/{workflow_id}/state")
async def get_state(workflow_id: str):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    try:
        state = await handle.query(PortalFlow.get_state)
        return asdict(state) if is_dataclass(state) else dict(state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/mfa")
async def provide_mfa(workflow_id: str, body: dict[str, Any]):
    code = body.get("code")
    if not code:
        raise HTTPException(status_code=422, detail="Missing 'code'")
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    try:
        await handle.signal(PortalFlow.provide_mfa, str(code))
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Signal failed: {type(e).__name__}: {e}")

    # Try to await result briefly; if not done, return 202
    try:
        result = await asyncio.wait_for(handle.result(), timeout=10)
        return {"result": result}
    except asyncio.TimeoutError:
        return {"status": "signal_sent", "message": "Workflow still running; check state later"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Workflow error: {type(e).__name__}: {e}")


@router.get("/{workflow_id}/result")
async def get_result(workflow_id: str):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    try:
        result = await asyncio.wait_for(handle.result(), timeout=1)
        return {"status": "completed", "result": result}
    except asyncio.TimeoutError:
        return {"status": "running"}
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}
    except asyncio.TimeoutError:
        return {"status": "signal_sent", "message": "Workflow still running; check state later"}
