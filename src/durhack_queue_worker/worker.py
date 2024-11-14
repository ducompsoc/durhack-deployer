import asyncio
import os
from pathlib import Path
from typing import override

import git
import pm2
import pnpm
from config import DurHackDeploymentConfig
from deployments import Deployment
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker


class DurHackQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[DurHackDeploymentConfig], *args, **kwargs):
        super().__init__(deployment.queue, deployment.config.repository, *args, **kwargs)

    @override
    async def on_push(self, payload: PushEvent) -> None:
        pm2_env = os.environ.copy()
        pm2_env["INSTANCE_NAME"] = self.config.instance_name

        pm2_ecosystem_file = Path(self.config.path, "ecosystem.config.cjs")
        previous_config = await pm2.read_config(pm2_ecosystem_file, env=pm2_env)

        await self.checkout(payload["head_commit"]["id"])

        await pnpm.install(self.config.path, "{server}...")
        await pnpm.exec(self.config.path, "prisma migrate deploy", "{server}")
        await pnpm.run(self.config.path, "generate", "{server}...")
        await pnpm.run(self.config.path, "build", "{server}...")

        async with asyncio.TaskGroup() as task_group:
            for app in previous_config.apps:
                task_group.create_task(pm2.stop(app.name))

        await pm2.restart(str(pm2_ecosystem_file), env=pm2_env)
        await pm2.save()
