from typing import TypedDict, NotRequired

from .hook_entity import HookEntity
from .simple_user_entity import SimpleUserEntity
from .repository_entity import RepositoryEntity

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
class PingEvent(TypedDict):
    hook: NotRequired[HookEntity]
    hook_id: NotRequired[int]
    organization: NotRequired[SimpleUserEntity]
    repository: NotRequired[RepositoryEntity]
    sender: NotRequired[SimpleUserEntity]
    zen: NotRequired[str]
