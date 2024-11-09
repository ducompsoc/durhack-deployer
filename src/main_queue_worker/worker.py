import asyncio
from pathlib import Path
from typing import override

from data_types import GitHubEvent
from definitions import project_root_dir
from deployments import lookup_event_deployment
from github_payload_types import PushEvent
from json_serialization import durhack_deployer_json_load
from queue_worker_base import QueueWorkerBase, run_worker
from queues import main_queue
from storage import persisted_event_exists, persist_handled_event

queue_directory = Path(project_root_dir, "queues")


class MainQueueWorker(QueueWorkerBase):
    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
        with open(queue_item_path) as queue_item_handle:
            event = durhack_deployer_json_load(queue_item_handle)

        if not isinstance(event, GitHubEvent):
            # log a message saying a queue item was invalid
            return

        if await persisted_event_exists(event):
            # log a message saying we are ignoring an event as it was previously processed
            return

        if event.type == "ping":
            await persist_handled_event(event)
            return

        if event.type == "push":
            await handle_push_event(event)
            return

        # should log a message here r.e. handling not implemented
        return


async def handle_push_event(event: GitHubEvent) -> None:
    assert event.type == "push"
    payload: PushEvent = event.payload
    deployment = lookup_event_deployment(payload)
    if deployment is None or not deployment.config.enabled:
        return
    # if we find an enabled deployment, add the event to its worker queue
    deployment.queue.push_event(event)


async def main() -> None:
    main_queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(MainQueueWorker, main_queue)


if __name__ == "__main__":
    asyncio.run(main())
