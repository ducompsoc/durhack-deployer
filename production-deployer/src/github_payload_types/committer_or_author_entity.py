from typing import TypedDict, NotRequired

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
type CommitterOrAuthorEntity = TypedDict(
    "GitHubCommitterOrAuthorEntity",
    {
        "date": NotRequired[str],
        "email": str | None,
        "name": str,
        "username": NotRequired[str],
    }
)
