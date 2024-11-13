from typing import override

import git
import systemctl
import uwsgi
from config import DeployerDeploymentConfig
from deployments import Deployment
from git import FileTreeDiff
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker


class DeployerQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[DeployerDeploymentConfig], *args, **kwargs):
        super().__init__(deployment.queue, deployment.config.repository, *args, **kwargs)

    @override
    async def on_push(self, payload: PushEvent, diff: FileTreeDiff) -> None:
        await git.checkout(self.config.path, payload["head_commit"]["id"], self._logger)
        await uwsgi.reload(self.config.uwsgi_config_path, self._logger)
        await systemctl.restart(self.config.systemd_unit_name, block=False, logger=self._logger)
