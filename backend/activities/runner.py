from __future__ import annotations

from typing import Any

from temporalio import activity


@activity.defn
async def run_steps(flow_yaml: str) -> dict[str, Any]:
    # Stub: validate YAML and return deterministic mock output
    # Real implementation will execute via Playwright
    return {"ok": True, "summary": "stubbed execution", "length": len(flow_yaml)}

