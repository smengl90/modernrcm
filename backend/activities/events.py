from __future__ import annotations

import json

import redis.asyncio as aioredis
from temporalio import activity

from ..app.settings import get_settings


@activity.defn
async def emit_event(event: dict) -> None:
    s = get_settings()
    r = aioredis.from_url(s.redis_url)
    try:
        await r.publish("events", json.dumps(event))
    finally:
        await r.close()
