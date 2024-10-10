from typing import TypedDict, NotRequired

from .hook_entity import HookEntity

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
type PingEvent = TypedDict(
    "GitHubPingEvent",
    {
        "hook": NotRequired[HookEntity],
        "hook_id": NotRequired[int],
        "organization": NotRequired[object],
        "repository": NotRequired[object],
        "sender": NotRequired[object],
        "zen": NotRequired[str],
    }
)
