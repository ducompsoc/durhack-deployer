from typing import TypedDict, NotRequired

from .commit_entity import CommitEntity
from .committer_or_author_entity import CommitterOrAuthorEntity
from .repository_entity import RepositoryEntity
from .simple_user_entity import SimpleUserEntity


# https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
class PushEvent(TypedDict):
    after: str
    base_ref: str | None
    before: str
    commits: list[CommitEntity]
    compare: str
    enterprise: NotRequired[object]
    forced: bool
    head_commit: CommitEntity
    installation: NotRequired[object]
    organization: NotRequired[SimpleUserEntity]
    pusher: CommitterOrAuthorEntity
    ref: str
    repository: RepositoryEntity
    sender: SimpleUserEntity
