from dataclasses import dataclass
from typing import Literal


@dataclass
class GitHubEvent:
    payload: dict
    type: Literal["ping", "push"] | str
    id: str
