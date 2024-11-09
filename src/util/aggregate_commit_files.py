from dataclasses import dataclass
from functools import reduce

from github_payload_types import CommitEntity


@dataclass
class _MutableFileTreeDiff:
    added: set[str]
    removed: set[str]
    modified: set[str]

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


def _apply_commit(accumulator: _MutableFileTreeDiff, commit: CommitEntity) -> _MutableFileTreeDiff:
    for path in commit["added"]:
        # added -> added: error
        assert path not in accumulator.added

        # removed -> added: modified
        if path in accumulator.removed:
            accumulator.removed.remove(path)
            accumulator.modified.add(path)
            continue

        # modified -> added: error
        assert path not in accumulator.modified

        # null -> added: added
        accumulator.added.add(path)

    for path in commit["removed"]:
        # added -> removed: null
        if path in accumulator.added:
            accumulator.added.remove(path)
            continue

        # removed -> removed: error
        assert path not in accumulator.removed

        # modified/null -> removed: removed
        accumulator.modified.discard(path)
        accumulator.removed.add(path)

    for path in commit["modified"]:
        # added -> modified: added
        if path in accumulator.added:
            continue

        # removed -> modified: error
        assert path not in accumulator.removed

        # modified/null -> modified: modified
        accumulator.modified.add(path)

    return accumulator


def aggregate_commit_files(commits: list[CommitEntity]) -> FileTreeDiff:
    if len(commits) == 0:
        return FileTreeDiff(frozenset(), frozenset(), frozenset())
    first_commit = commits[0]
    accumulator = _MutableFileTreeDiff(
        set(first_commit["added"]),
        set(first_commit["removed"]),
        set(first_commit["modified"]),
    )
    result = reduce(_apply_commit, commits[1:], accumulator)
    return result.freeze()

__all__ = ("aggregate_commit_files", "FileTreeDiff",)
