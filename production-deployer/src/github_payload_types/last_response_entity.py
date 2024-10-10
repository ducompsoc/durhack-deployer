from typing import TypedDict, NotRequired

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
type LastResponseEntity = TypedDict(
    "GitHubLastResponseEntity",
    {
        "code": int | None,
        "status": str | None,
        "message": str | None,
    }
)
