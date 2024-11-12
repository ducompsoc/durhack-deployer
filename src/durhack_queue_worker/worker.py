import asyncio
import os
from pathlib import Path
from typing import override

import git
import pm2
import pnpm
from config import DurHackDeploymentConfig
from data_types import GitHubEvent
from deployments import Deployment
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker
from storage import persisted_event_exists, persist_handled_event


class DurHackQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[DurHackDeploymentConfig], *args, **kwargs):
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

            pm2_env = os.environ.copy()
            pm2_env["INSTANCE_NAME"] = self.config.instance_name

            pm2_ecosystem_file = Path(self.config.path, "ecosystem.config.cjs")
            previous_config = await pm2.read_config(pm2_ecosystem_file, env=pm2_env)

            await git.fetch(self.config.path, self._logger)
            file_tree_diff = await git.diff(self.config.path, "HEAD", payload["head_commit"]["id"])
            await git.checkout(self.config.path, payload["head_commit"]["id"], self._logger)

            await pnpm.install(self.config.path, "{server}...")
            await pnpm.exec(self.config.path, "prisma migrate deploy", "{server}")
            await pnpm.run(self.config.path, "generate", "{server}...")
            await pnpm.run(self.config.path, "build", "{server}...")

            async with asyncio.TaskGroup() as task_group:
                for app in previous_config.apps:
                    task_group.create_task(pm2.stop(app.name))

            await pm2.restart(str(pm2_ecosystem_file), env=pm2_env)
            await pm2.save()

            await persist_handled_event(event)
