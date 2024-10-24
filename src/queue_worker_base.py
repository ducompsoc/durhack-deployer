import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager
from pathlib import Path
import signal
from typing import override, Type

from watchdog.events import FileClosedEvent

from aio_watchdog import AIOWatchdog, AIOEventHandler
from queues import Queue


class QueueDirectoryListener(AIOEventHandler):
    def __init__(
        self,
        match_queue_item_predicate: Callable[[Path], bool],
        notify_callback: Callable[[Path], None],
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        super().__init__(loop=loop)
        self.match_queue_item_predicate = match_queue_item_predicate
        self.notify_callback = notify_callback

    @override
    async def on_closed(self, event: FileClosedEvent) -> None:
        path = Path(event.src_path)
        if not self.match_queue_item_predicate(path):
            return
        self.notify_callback(path)


class QueueWorkerBase:
    """
    Base class for queue workers. Performs no specific event item handling.
    This should be subclassed and its `process_queue_item` implementation overridden to create more useful queue workers.
    """

    def __init__(
        self,
        queue: Queue,
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        self._loop = loop if loop is not None else asyncio.get_running_loop()
        self.queue = queue
        self.queue_directory_listener = QueueDirectoryListener(
            self.is_queue_item,
            self.create_queue_item_task,
            loop=loop,
        )
        self.queue_item_tasks: set[asyncio.Task[None]] = set()

    @classmethod
    def is_queue_item(cls, path: Path) -> bool:
        if path.name.startswith("."): return False
        if path.suffix != ".json": return False
        return True

    def create_queue_item_task(self, queue_item_path: Path) -> None:
        process_queue_item_task = self._loop.create_task(self.process_queue_item(queue_item_path))

        async def cleanup_after_processing():
            await process_queue_item_task
            queue_item_path.unlink(missing_ok=True)
            self.queue_item_tasks.remove(asyncio.current_task())

        cleanup_after_processing_task = self._loop.create_task(cleanup_after_processing())
        self.queue_item_tasks.add(cleanup_after_processing_task)

    def create_tasks_for_existing_queue_items(self) -> None:
        candidates = self.queue.path.glob("*.json")
        filtered_candidates = filter(self.is_queue_item, candidates)

        def filename(path: Path) -> str:
            return path.name

        ordered_candidates = sorted(filtered_candidates, key=filename)
        for candidate in ordered_candidates:
            self.create_queue_item_task(candidate)

    async def process_queue_item(self, queue_item_path: Path) -> None:
        pass

    @asynccontextmanager
    async def run(self):
        try:
            self.create_tasks_for_existing_queue_items()
            with AIOWatchdog(self.queue.path, event_handler=self.queue_directory_listener):
                yield
        finally:
            if self.queue_item_tasks:
                await asyncio.wait(self.queue_item_tasks)


async def run_worker(worker_factory: Type[QueueWorkerBase], queue: Queue, *args, **kwargs) -> None:
    loop = asyncio.get_running_loop()
    interrupted = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, interrupted.set_result, None)

    queue.path.mkdir(parents=True, exist_ok=True)
    worker = worker_factory(queue, *args, **kwargs, loop=loop)
    async with worker.run():
        await interrupted


async def main() -> None:
    queue = Queue("base")
    await run_worker(QueueWorkerBase, queue)


if __name__ == "__main__":
    asyncio.run(main())
