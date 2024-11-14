from typing import TypedDict, Literal, NotRequired, Self

class CrossplaneFileParseError(TypedDict):
    error: str
    line: int

class CrossplaneDirectiveParseResult(TypedDict):
    directive: str
    line: int
    args: list[str]
    block: NotRequired[list[Self]]


class CrossplaneFileParseResult(TypedDict):
    file: str
    status: Literal["ok", "failed"]
    errors: list[CrossplaneFileParseError]
    parsed: list[CrossplaneDirectiveParseResult]


class CrossplaneParseError(CrossplaneFileParseError):
    file: str


class CrossplaneParseResult(TypedDict):
    status: Literal["ok", "failed"]
    errors: list[CrossplaneParseError]
    config: list[CrossplaneFileParseResult]
