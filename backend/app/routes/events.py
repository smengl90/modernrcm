from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import StreamingResponse

from ..events.bus import get_bus


router = APIRouter()


async def _event_stream(run_id: str | None = None, batch_id: str | None = None) -> AsyncIterator[bytes]:
    bus = get_bus()
    async for evt in bus.subscribe():
        if run_id and evt.get("run_id") != run_id:
            continue
        if batch_id and evt.get("batch_id") != batch_id:
            continue
        data = json.dumps(evt)
        yield f"data: {data}\n\n".encode()
        await asyncio.sleep(0)  # cooperative


@router.get("/events")
async def events(request: Request, run_id: str | None = None, batch_id: str | None = None):
    return StreamingResponse(_event_stream(run_id, batch_id), media_type="text/event-stream")

