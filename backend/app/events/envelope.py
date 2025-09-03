from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class Event:
    type: str
    payload: dict[str, Any]
    run_id: str | None = None
    batch_id: str | None = None
    source: str = "api"
    ts: str = datetime.now(timezone.utc).isoformat()

    def dict(self) -> dict[str, Any]:
        return asdict(self)

