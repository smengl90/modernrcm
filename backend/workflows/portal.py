from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio import activity


@dataclass
class State:
    waiting_mfa: bool = False
    mfa_code: str | None = None
    output: dict[str, Any] | None = None


@workflow.defn
class PortalFlow:
    def __init__(self) -> None:
        self.state = State()

    @workflow.signal
    def provide_mfa(self, code: str) -> None:
        self.state.mfa_code = code
        self.state.waiting_mfa = False

    @workflow.query
    def get_state(self) -> State:
        return self.state

    @workflow.run
    async def run(self, flow_id: str, steps: list[dict]) -> dict:
        # Emit a breakpoint requiring MFA
        await workflow.execute_activity(
            "emit_event",
            {"type": "breakpoint.mfa.requested", "payload": {"flow_id": flow_id}},
            start_to_close_timeout=timedelta(seconds=30),
        )
        self.state.waiting_mfa = True
        # Wait up to 5 minutes for MFA
        ok = await workflow.wait_condition(lambda: not self.state.waiting_mfa, timeout=timedelta(seconds=300))
        if not ok:
            raise RuntimeError("MFA not provided in time")
        # Execute stubbed steps (real execution will be in activities)
        # Return deterministic mock for now
        self.state.output = {"flow_id": flow_id, "steps": len(steps), "status": "ok"}
        await workflow.execute_activity(
            "emit_event",
            {"type": "run.succeeded", "payload": {"flow_id": flow_id}},
            start_to_close_timeout=timedelta(seconds=30),
        )
        return self.state.output
