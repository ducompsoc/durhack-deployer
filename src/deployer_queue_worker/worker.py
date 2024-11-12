import asyncio
from pathlib import Path
from typing import override

import pm2
import uwsgi
from config import DeployerDeploymentConfig
from data_types import GitHubEvent
from deployments import Deployment
import git
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
            await pm2.restart(self.config.instance_name, Path(self.config.path, "ecosystem.config.cjs"), self._logger)

            await persist_handled_event(event)
