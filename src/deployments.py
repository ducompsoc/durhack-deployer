from dataclasses import dataclass, field

from config import config, DeploymentConfig
from github_payload_types import PushEvent
from queues import Queue


@dataclass(eq=True, frozen=True)
class DeploymentSpecifier:
    repository_full_name: str
    branch_name: str


@dataclass
class Deployment[Config: DeploymentConfig]:
    slug: str
    config: Config

    _queue: Queue | None = field(init=False)

    def __post_init__(self):
        self._queue = None

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
    return deployments.get(slug, None)


def lookup_deployment_by_spec(spec: DeploymentSpecifier) -> Deployment | None:
    return deployment_by_spec.get(spec, None)


def lookup_event_deployment(event_payload: PushEvent) -> Deployment | None:
    ref = event_payload["ref"]
    if not ref.startswith("refs/heads/"):
        return None
    branch_name = ref[11:]

    spec = DeploymentSpecifier(
        event_payload["repository"]["full_name"],
        branch_name,
    )
    return lookup_deployment_by_spec(spec)
