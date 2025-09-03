from __future__ import annotations

import asyncio
from temporalio.client import Client
from ..app.settings import get_settings


_client: Client | None = None


async def get_temporal_client() -> Client:
    global _client
    if _client is None:
        s = get_settings()
        last_err: Exception | None = None
        for attempt in range(30):
            try:
                _client = await Client.connect(s.temporal_target, namespace=s.temporal_namespace)
                break
            except Exception as e:  # retry until Temporal is ready/DNS resolves
                last_err = e
                await asyncio.sleep(2)
        else:
            raise last_err or RuntimeError("Failed to connect to Temporal")
    return _client
