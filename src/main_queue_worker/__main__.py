import asyncio
import argparse

from queue_worker_base import run_worker
from queues import main_queue

from .worker import MainQueueWorker


parser = argparse.ArgumentParser(
    prog="main-queue-worker",
    description="Handles queued 'push' events from various DurHack repositories by piping them to the appropriate worker queue(s).",
)


async def main() -> None:
    parser.parse_args()
    main_queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(MainQueueWorker, main_queue)


if __name__ == '__main__':
    asyncio.run(main())
