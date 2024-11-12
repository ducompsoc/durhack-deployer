import asyncio
from typing import override

import git
import systemctl
import uwsgi
from config import DeployerDeploymentConfig
from data_types import GitHubEvent
from deployments import Deployment
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker
from storage import persisted_event_exists, persist_handled_event


class DeployerQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[DeployerDeploymentConfig], *args, **kwargs):
        super().__init__(deployment.queue, deployment.config.repository, *args, **kwargs)
        self.deploy_lock = asyncio.Lock()
        self.config = deployment.config

    @override
    async def process_github_event(self, event: GitHubEvent) -> None:
        assert event.type == "push"
        payload: PushEvent = event.payload

        async with self.deploy_lock:
            if await persisted_event_exists(event):
                # log a message saying we are ignoring an event as it was previously processed
                return

            await git.fetch(self.config.path, self._logger)
            file_tree_diff = await git.diff(self.config.path, "HEAD", payload["head_commit"]["id"])
            await git.checkout(self.config.path, payload["head_commit"]["id"], self._logger)

            await uwsgi.reload(self.config.uwsgi_config_path, self._logger)
            await systemctl.restart(self.config.systemd_unit_name, block=False, logger=self._logger)

            await persist_handled_event(event)
