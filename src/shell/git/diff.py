from dataclasses import dataclass, field
from logging import Logger, getLogger
from pathlib import Path
from typing import Literal, Callable

from util import async_subprocess

from ._set_env import set_env

# https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---diff-filterACDMRTUXB82308203
type DiffStatusLetter = Literal[
    "A",  # Added
    "C",  # Copied - won't show up because --no-renames
    "D",  # Deleted
    "M",  # Modified
    "R",  # Renamed - won't show up because --no-renames
    "T",  # Type changed
    "U",  # Unmerged
    "X",  # Unknown
    "B",  # pairing Broken
]


@dataclass
class _MutableFileTreeDiff:
    added: set[str] = field(default_factory=set)
    removed: set[str] = field(default_factory=set)
    modified: set[str] = field(default_factory=set)

    def freeze(self):
        return FileTreeDiff(
            frozenset(self.added),
            frozenset(self.removed),
            frozenset(self.modified),
        )


@dataclass(frozen=True)
class FileTreeDiff:
    added: frozenset[str]
    removed: frozenset[str]
    modified: frozenset[str]


_status_to_action_map: dict[DiffStatusLetter, Callable[[_MutableFileTreeDiff, str], None]] = {
    "A": lambda file_diff, path: file_diff.added.add(path),
    "D": lambda file_diff, path: file_diff.removed.add(path),
    "M": lambda file_diff, path: file_diff.modified.add(path),
    "T": lambda file_diff, path: file_diff.modified.add(path),
}


async def diff(
    path: Path,
    from_ref: str,
    to_ref: str,
    logger: Logger | None = None,
) -> FileTreeDiff:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"git -C {path} -P diff --no-renames --diff-filter=ADMT --name-status '{from_ref}' '{to_ref}'",
        set_env(),
    )

    if result.exit_code != 0:
        raise Exception(f"`git diff` exited with status {result.exit_code}; {result.stderr}")

    file_tree_diff = _MutableFileTreeDiff()
    for line in result.stdout.splitlines():
        status: DiffStatusLetter
        path: str
        status, path = line.split("\t")
        action = _status_to_action_map[status]
        action(file_tree_diff, path)

    return file_tree_diff.freeze()
