from typing import TypedDict, NotRequired

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
class LastResponseEntity(TypedDict):
    code: int | None
    status: str | None
    message: str | None
