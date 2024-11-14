from typing import override

import systemctl
import uwsgi
from config import DeployerDeploymentConfig
from deployments import Deployment
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker


class DeployerQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[DeployerDeploymentConfig], *args, **kwargs):
        super().__init__(deployment, *args, **kwargs)

    @override
    async def on_push(self, payload: PushEvent) -> None:
        await self.checkout(payload["head_commit"]["id"])
        await self.deploy()

    async def on_init(self) -> None:
        await self.deploy()

    async def deploy(self) -> None:
        # todo: pipenv install
        await uwsgi.reload(self.config.uwsgi_config_path, self._logger)
        await systemctl.restart(self.config.systemd_unit_name, block=False, logger=self._logger)
