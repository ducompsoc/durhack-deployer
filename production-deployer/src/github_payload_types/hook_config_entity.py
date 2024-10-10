from typing import TypedDict, NotRequired

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
class HookConfigEntity(TypedDict):
    content_type: NotRequired[str]
    insecure_ssl: NotRequired[str]
    secret: NotRequired[str]
    url: NotRequired[str]
