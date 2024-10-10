from typing import TypedDict, NotRequired

from .commit_entity import CommitEntity
from .committer_or_author_entity import CommitterOrAuthorEntity

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
type PushEvent = TypedDict(
    "GitHubPushEvent",
    {
        "after": str,
        "base_ref": str | None,
        "before": str,
        "commits": list[CommitEntity],
        "compare": str,
        "enterprise": NotRequired[object],
        "forced": bool,
        "head_commit": CommitEntity,
        "installation": NotRequired[object],
        "organization": NotRequired[object],
        "pusher": CommitterOrAuthorEntity,
        "ref": str,
        "repository": object,
        "sender": object,
    }
)
