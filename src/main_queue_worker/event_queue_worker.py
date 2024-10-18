from data_types import GitHubEvent
from storage import async_session, PersistedEvent


async def persist_handled_event(event: GitHubEvent) -> None:
    async with async_session() as session:
        persisted_event = PersistedEvent(id=event.id)
        session.add(persisted_event)
        await session.commit()


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