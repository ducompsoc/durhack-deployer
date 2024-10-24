from dataclasses import dataclass, field

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

    _queue: Queue = field(init=False)

    @property
    def queue(self):
        if self._queue is not None:
            return self._queue
        self._queue = Queue(self.slug)
        return self._queue


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
