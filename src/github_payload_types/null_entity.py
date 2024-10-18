from typing import TypedDict, Literal


class NullEntity(TypedDict, total=False):
    type: Literal["null"]
