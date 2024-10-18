from typing import TypedDict, NotRequired, Literal, Required

from .null_entity import NullEntity
from .repository_permissions_entity import RepositoryPermissionsEntity
from .repository_simple_code_of_conduct_entity import RepositorySimpleCodeOfConductEntity
from .repository_security_and_analysis_entity import RepositorySecurityAndAnalysisEntity
from .repository_simple_license_entity import RepositorySimpleLicenseEntity
from .simple_user_entity import SimpleUserEntity


class RepositorySimpleUserEntity(SimpleUserEntity):
    starred_at: NotRequired[str]    


# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class _RepositoryEntityBase(TypedDict, total=False):
    id: Required[int]
    node_id: Required[str]
    name: Required[str]
    full_name: Required[str]
    owner: Required[RepositorySimpleUserEntity]
    license: Required[NullEntity | RepositorySimpleLicenseEntity]
    forks: Required[int]
    permissions: RepositoryPermissionsEntity
    private: Required[bool] 
    html_url: Required[str]
    description: str | None
    fork: Required[bool]
    url: Required[str]
    archive_url: str
    assignees_url: Required[str]
    blobs_url: Required[str]
    branches_url: Required[str]
    collaborators_url: Required[str]
    comments_url: Required[str]
    commits_url: Required[str]
    compare_url: Required[str]
    contents_url: Required[str]
    contributors_url: Required[str]
    deployments_url: Required[str]
    downloads_url: Required[str]
    events_url: Required[str]
    forks_url: Required[str]
    git_commits_url: Required[str]
    git_refs_url: Required[str]
    git_tags_url: Required[str]
    git_url: Required[str]
    issue_comment_url: Required[str]
    issue_events_url: Required[str]
    issues_url: Required[str]
    keys_url: Required[str]
    labels_url: Required[str]
    languages_url: Required[str]
    merges_url: Required[str]
    milestones_url: Required[str]
    notifications_url: Required[str]
    pulls_url: Required[str]
    releases_url: Required[str]
    ssh_url: Required[str]
    stargazers_url: Required[str]
    statuses_url: Required[str]
    subscribers_url: Required[str]
    subscription_url: Required[str]
    tags_url: Required[str]
    teams_url: Required[str]
    trees_url: Required[str]
    clone_url: Required[str]
    mirror_url: Required[str | None]
    hooks_url: Required[str]
    svn_url: Required[str]
    homepage: Required[str | None]
    language: Required[str | None]
    forks_count: Required[int]
    stargazers_count: Required[int]
    watchers_count: Required[int]
    size: Required[int]
    default_branch: Required[str]
    open_issues_count: Required[int]
    is_template: bool
    topics: list[str]
    has_issues: Required[bool]
    has_projects: Required[bool]
    has_wiki: Required[bool]
    has_pages: Required[bool]
    has_downloads: bool | None  # deprecated feature; not required property
    has_discussions: Required[bool]  # I think it is a mistake that `has_discussions` is missing from nested repository objects 'requiredProperties'
    archived: Required[bool]
    disabled: Required[bool]
    visibility: Literal["public", "private", "internal"]
    pushed_at: Required[str]
    created_at: Required[str]
    updated_at: Required[str]
    allow_rebase_merge: bool
    temp_clone_token: str | None
    allow_squash_merge: bool
    allow_auto_merge: bool
    delete_branch_on_merge: bool
    allow_update_branch: bool
    use_squash_pr_title_as_default: bool
    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"]
    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"]
    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"]
    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"]
    allow_merge_commit: bool
    allow_forking: bool
    web_commit_signoff_required: bool
    open_issues: Required[int]
    watchers: Required[int]
    master_branch: str
    anonymous_access_enabled: bool
    

class RepositoryEntity(_RepositoryEntityBase, total=False):
    starred_at: str


class FullRepositoryEntity(_RepositoryEntityBase, total=False):
    code_of_conduct: RepositorySimpleCodeOfConductEntity  # **
    security_and_analysis: RepositorySecurityAndAnalysisEntity | None  # **
    custom_properties: dict[str, object]  # **
    template_repository: NullEntity | RepositoryEntity  # **
    subscribers_count: Required[int]
    network_count: Required[int]
    organization: NullEntity | RepositorySimpleUserEntity
    parent: RepositoryEntity
    source: RepositoryEntity
