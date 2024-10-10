from typing import TypedDict, NotRequired


# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class SimpleUserEntity(TypedDict):
    name: NotRequired[str | None]
    email: NotRequired[str | None]
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str | None
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
