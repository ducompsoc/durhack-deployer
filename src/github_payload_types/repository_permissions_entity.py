from typing import TypedDict, Required


class RepositoryPermissionsEntity(TypedDict, total=False):
    admin: Required[bool]
    maintain: bool
    push: Required[bool]
    triage: bool
    pull: Required[bool]
