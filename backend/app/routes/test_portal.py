from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from fastapi import APIRouter, HTTPException

from ...workflows.client import get_temporal_client
from ...workflows.portal import PortalFlow
from ...app.settings import get_settings
from temporalio.exceptions import WorkflowAlreadyStartedError


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
        )
    except WorkflowAlreadyStartedError:
        handle = client.get_workflow_handle(workflow_id)

    # Query state for waiting_mfa
    try:
        state = await handle.query(PortalFlow.get_state)
        state_dict = asdict(state) if is_dataclass(state) else dict(state)
    except Exception:
        state_dict = {}

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
    await handle.signal(PortalFlow.provide_mfa, str(code))
    result = await handle.result()
    return {"result": result}
