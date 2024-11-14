import asyncio
import os
from pathlib import Path
from typing import override

import pm2
from pm2.read_config import PM2App
import pnpm
from config import DurHackDeploymentConfig
from deployments import Deployment
from github_payload_types import PushEvent
from github_repository_queue_worker import GitHubRepositoryQueueWorker


class DurHackQueueWorker(GitHubRepositoryQueueWorker):
    def __init__(self, deployment: Deployment[DurHackDeploymentConfig], *args, **kwargs):
        super().__init__(deployment, *args, **kwargs)
        self.pm2_ecosystem_file = Path(self.config.path, "ecosystem.config.cjs")

    def get_pm2_env(self):
        pm2_env = os.environ.copy()
        pm2_env["INSTANCE_NAME"] = self.config.instance_name
        return pm2_env

    @override
    async def on_push(self, payload: PushEvent) -> None:
        pm2_env = self.get_pm2_env()

        previous_config = None
        if self.pm2_ecosystem_file.exists():
            previous_config = await pm2.read_config(self.pm2_ecosystem_file, env=pm2_env)

        await self.checkout(payload["head_commit"]["id"])
        await self.install_and_build()

        if previous_config is not None:
            await self.delete_apps(previous_config.apps)

        await pm2.restart(str(self.pm2_ecosystem_file), env=pm2_env)
        await pm2.save()

    async def on_init(self) -> None:
        await self.install_and_build()
        pm2_env = self.get_pm2_env()
        await pm2.restart(str(self.pm2_ecosystem_file), env=pm2_env)
        await pm2.save()

    async def delete_apps(self, apps: list[PM2App]):
        async with asyncio.TaskGroup() as task_group:
            for app in apps:
                task_group.create_task(pm2.delete(app.name))

    async def install_and_build(self) -> None:
        await pnpm.install(self.config.path, "{server}...")
        await pnpm.exec(self.config.path, "prisma migrate deploy", "{server}")
        await pnpm.run(self.config.path, "generate", "{server}...")
        await pnpm.run(self.config.path, "build", "{server}...")
