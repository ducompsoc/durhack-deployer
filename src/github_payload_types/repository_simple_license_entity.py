from typing import TypedDict, Required


class RepositorySimpleLicenseEntity(TypedDict, total=False):
    key: Required[str]
    name: Required[str]
    url: Required[str | None]
    spdx_id: Required[str | None]
    node_id: Required[str]
    html_url: str
