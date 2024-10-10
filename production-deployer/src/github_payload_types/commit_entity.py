from typing import TypedDict, NotRequired

from .committer_or_author_entity import CommitterOrAuthorEntity

# https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
type CommitEntity = TypedDict(
    "GitHubCommitEntity",
    {
        "added": NotRequired[list[str]],
        "author": CommitterOrAuthorEntity,
        "committer": CommitterOrAuthorEntity,
        "distinct": bool,
        "id": str,
        "message": str,
        "modified": NotRequired[list[str]],
        "removed": NotRequired[list[str]],
        "timestamp": str,
        "tree_id": str,
        "url": str,
    }
)
