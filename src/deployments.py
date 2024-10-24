from dataclasses import dataclass

from config import config, DeploymentConfig
from github_payload_types import PushEvent
from queues import Queue


@dataclass(eq=True, frozen=True)
class DeploymentSpecifier:
    repository_full_name: str
    branch_name: str


@dataclass
class Deployment:
    slug: str
    config: DeploymentConfig

    @property
    def queue(self) -> Queue:
        return Queue(self.slug)


deployments = {slug: Deployment(slug, config) for slug, config in config.deployments.items()}
deployment_by_spec = {
    DeploymentSpecifier(deployment.config.repository, deployment.config.branch): deployment for deployment in deployments.values()
}


def lookup_deployment_by_slug(slug: str) -> Deployment | None:
    try:
        return deployments[slug]
    except KeyError:
        return None


def lookup_deployment_by_spec(spec: DeploymentSpecifier) -> Deployment | None:
    try:
        return deployment_by_spec[spec]
    except KeyError:
        return None


def lookup_event_deployment(event_payload: PushEvent) -> Deployment | None:
    base_ref = event_payload["base_ref"]
    if not base_ref.startswith("refs/heads/"):
        return None
    branch_name = base_ref[11:]

    spec = DeploymentSpecifier(
        event_payload["repository"]["full_name"],
        branch_name,
    )
    return lookup_deployment_by_spec(spec)
