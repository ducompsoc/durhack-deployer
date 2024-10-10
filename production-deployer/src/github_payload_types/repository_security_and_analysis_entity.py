from typing import TypedDict, Literal


class ActivityStateEntity(TypedDict, total=False):
    status: Literal["enabled", "disabled"]


class RepositorySecurityAndAnalysisEntity(TypedDict, total=False):
    advanced_security: ActivityStateEntity
    dependabot_security_updates: ActivityStateEntity
    secret_scanning: ActivityStateEntity
    secret_scanning_push_protection: ActivityStateEntity
    secret_scanning_non_provider_patterns: ActivityStateEntity
