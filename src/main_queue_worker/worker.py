import asyncio
from pathlib import Path
from time import time_ns
from typing import override, TextIO

from sqlalchemy import exists

from data_types import GitHubEvent
from definitions import project_root_dir
from deployments import lookup_event_deployment
from github_payload_types import PushEvent
from json_serialization import durhack_deployer_json_load, durhack_deployer_json_dump
from queue_worker_base import QueueWorkerBase, run_worker
from storage import async_session, PersistedEvent


# this is here for now so that I don't forget how to do it, but checking for & persisting handled events does NOT fall within the
# main queue worker's set of responsibilities (except for 'ping' events);
# instead, deployment-specific workers are responsible for these tasks.
async def persist_handled_event(event: GitHubEvent) -> None:
    async with async_session() as session:
        persisted_event = PersistedEvent(id=event.id)
        session.add(persisted_event)
        await session.commit()


async def persisted_event_exists(event_id: str) -> bool:
    async with async_session() as session:
        return await session.scalar(
            exists()
            .where(PersistedEvent.id == event_id)
            .select()
        )


queue_directory = Path(project_root_dir, "queues")


class MainQueueWorker(QueueWorkerBase):
    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
        with open(queue_item_path) as queue_item_handle:
            event = durhack_deployer_json_load(queue_item_handle)

        if not isinstance(event, GitHubEvent):
            # log a message saying a queue item was invalid
            return

        if persisted_event_exists(event.id):
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
    if deployment is None:
        return
    # if we find a deployment, add the event to its worker queue
    deployment_queue_dir = Path(queue_directory, deployment.slug)
    deployment_queue_dir.mkdir(parents=True, exist_ok=True)
    event_item_filepath = Path(deployment_queue_dir, f"${time_ns()}.json")
    with open(event_item_filepath, "x") as event_item_handle:
        durhack_deployer_json_dump(event, event_item_handle)


async def main() -> None:
    queue_dir = Path(queue_directory, "main")
    queue_dir.mkdir(parents=True, exist_ok=True)
    await run_worker(MainQueueWorker, queue_dir)


if __name__ == "__main__":
    asyncio.run(main())
