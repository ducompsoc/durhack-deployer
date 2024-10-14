from dataclasses import dataclass
from typing import Literal


@dataclass
class GitHubEvent:
    payload: object
    type: Literal["ping", "push"] | str
    id: str
