from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

import redis.asyncio as aioredis

from ..settings import get_settings


class EventBus:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or get_settings().redis_url
        self._redis = aioredis.from_url(self.url)
        self._channel = "events"

    async def publish(self, message: dict) -> None:
        await self._redis.publish(self._channel, json.dumps(message))

    async def subscribe(self) -> AsyncIterator[dict]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._channel)
        try:
            async for msg in pubsub.listen():
                if msg.get("type") == "message":
                    data = json.loads(msg["data"])  # type: ignore[index]
                    yield data
        finally:
            await pubsub.unsubscribe(self._channel)
            await pubsub.close()

    async def close(self):
        await self._redis.close()


_bus: EventBus | None = None


def get_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus

