from typing import TypedDict, NotRequired, Literal, Self

from .null_entity import NullEntity
from .repository_permissions_entity import RepositoryPermissionsEntity
from .repository_simple_license_entity import RepositorySimpleLicenseEntity
from .simple_user_entity import SimpleUserEntity


class RepositorySimpleUserEntity(SimpleUserEntity):
    starred_at: NotRequired[str]


# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class RepositoryEntity(TypedDict, total=False):
    id: int
    node_id: str
    name: str
    full_name: str
    owner: RepositorySimpleUserEntity
    private: bool
    html_url: str
    description: str | None
    fork: bool
    url: str
    archive_url: str
    assignees_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    deployments_url: str
    downloads_url: str
    events_url: str
    forks_url: str
    git_comments_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str
    merges_url: str
    milestones_url: str
    notifications_url: str
    pulls_url: str
    releases_url: str
    ssh_url: str
    stargazers_url: str
    statuses_url: str
    subscribers_url: str
    subscription_url: str
    tags_url: str
    teams_url: str
    trees_url: str
    clone_url: str
    mirror_url: str | None
    hooks_url: str
    svn_url: str
    homepage: str | None
    language: str | None
    forks_count: int
    stargazers_count: int
    watchers_count: int
    size: int
    default_branch: str
    open_issues_count: str
    is_template: bool
    topics: list[str]
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    has_discussions: bool
    archived: bool
    disabled: bool
    visibility: Literal["public", "private", "internal"]
    pushed_at: str
    created_at: str
    updated_at: str
    permissions: RepositoryPermissionsEntity
    allow_rebase_merge: bool
    template_repository: NullEntity | Self
    temp_clone_token: str | None
    allow_squash_merge: bool
    allow_auto_merge: bool
    delete_branch_on_merge: bool
    allow_merge_commit: bool
    allow_update_branch: bool
    use_squash_pr_title_as_default: bool
    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"]
    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"]
    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"]
    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"]
    allow_forking: bool
    web_commit_signoff_required: bool
    subscribers_count: int
    network_count: int
    license: NullEntity | RepositorySimpleLicenseEntity
    organization: NullEntity | RepositorySimpleUserEntity
    parent:



