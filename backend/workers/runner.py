from __future__ import annotations

import asyncio

from temporalio.worker import Worker

from ..app.settings import get_settings
from ..workflows.client import get_temporal_client
from ..workflows.portal import PortalFlow
from ..activities.runner import run_steps
from ..activities.events import emit_event


async def main():
    s = get_settings()
    client = await get_temporal_client()
    worker = Worker(
        client,
        task_queue=s.temporal_task_queue,
        workflows=[PortalFlow],
        activities=[run_steps, emit_event],
    )
    print("Worker started", flush=True)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
