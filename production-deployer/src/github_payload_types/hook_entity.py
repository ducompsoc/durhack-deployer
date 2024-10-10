from typing import TypedDict, NotRequired, Literal

from .hook_config_entity import HookConfigEntity
from .last_response_entity import LastResponseEntity

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
type HookEntity = TypedDict(
    "GitHubHookEntity",
    {
        "active": bool,
        "app_id": NotRequired[int],
        "config": HookConfigEntity,
        "created_at": str,
        "deliveries_url": NotRequired[str],
        "events": list[str],
        "id": int,
        "last_response": NotRequired[LastResponseEntity],
        "name": Literal['web'],
        "ping_url": NotRequired[str],
        "test_url": NotRequired[str],
        "type": str,
        "updated_at": str,
        "url": NotRequired[str],
    }
)
