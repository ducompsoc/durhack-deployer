from typing import override
from pathlib import Path

from data_types import GitHubEvent
from json_serialization import durhack_deployer_json_load
from queue_worker_base import QueueWorkerBase
from storage import async_session, PersistedEvent


# this is here for now so that I don't forget how to do it, but checking for & persisting handled events does NOT fall within the
# main queue worker's set of responsibilities; instead, deployment-specific workers are responsible for these tasks.
async def persist_handled_event(event: GitHubEvent) -> None:
    async with async_session() as session:
        persisted_event = PersistedEvent(id=event.id)
        session.add(persisted_event)
        await session.commit()


class MainQueueWorker(QueueWorkerBase):
    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
        with open(queue_item_path) as queueItemHandle:
            queue_item_payload = durhack_deployer_json_load(queueItemHandle)


async def handle_event(event: GitHubEvent) -> None:
    pass
    # Check the event ID (`X-GitHub-Delivery` request header) against persistent storage of 'already processed' events
    # if the event ID is known (i.e. has already been processed), we stop processing the event (as it could be a replay attack)

    # we need to decide what to do based on the event type.
    # in practise, the webhook should only ever receive two event types:
    # - `push` (when commits are pushed)
    # - `ping` (when the webhook is initially connected)
    # but we shouldn't assume that other event types will never be sent, and act accordingly (e.g. respond 'NOT IMPLEMENTED')
    if event.type == "ping":
        await handle_ping_event(event)
        await persist_handled_event(event)
        return

    if event.type == "push":
        await handle_push_event(event)
        await persist_handled_event(event)
        return

    # once the event has been handled, we add the event ID to persistent storage


async def handle_push_event(push_event: GitHubEvent) -> None:
    pass


async def handle_ping_event(ping_event: GitHubEvent) -> None:
    pass

