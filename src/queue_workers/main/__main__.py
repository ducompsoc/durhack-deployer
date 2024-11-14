import asyncio
import argparse
import signal

from queue_worker_base import run_worker
from queues import main_queue
from util.async_interrupt import create_interrupt_future

from .worker import MainQueueWorker


parser = argparse.ArgumentParser(
    prog="main-queue-worker",
    description="Handles queued 'push' events from various DurHack repositories by piping them to the appropriate worker queue(s).",
)

parser.add_argument(
    "-s",
    "--supervised",
    dest="supervised",
    action="store_true",
)


class MainArgNamespace(argparse.Namespace):
    supervised: bool

    def create_until_future(self):
        if self.supervised:
            return create_interrupt_future(signals=[signal.SIGTERM])
        return create_interrupt_future(signals=[signal.SIGINT, signal.SIGTERM])


async def main() -> None:
    args = parser.parse_args(None, MainArgNamespace())
    main_queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(MainQueueWorker, main_queue, until=args.create_until_future())


if __name__ == '__main__':
    asyncio.run(main())
