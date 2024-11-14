import asyncio
from os import getenv
from pathlib import Path
from typing import override

import git
import github
from data_types import GitHubEvent
from deployments import Deployment
from git import FileTreeDiff
from github_payload_types import PushEvent
from json_serialization import durhack_deployer_json_load
from queue_worker_base import QueueWorkerBase
from storage import persisted_event_exists, persist_handled_event


class GitHubRepositoryQueueWorker(QueueWorkerBase):
    def __init__(self, deployment: Deployment, *args, **kwargs):
        super().__init__(deployment.queue, *args, **kwargs)
        self.config = deployment.config
        self.repository_full_name = deployment.config.repository
        self.deploy_lock = asyncio.Lock()

    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
        with open(queue_item_path) as queue_item_handle:
            event = durhack_deployer_json_load(queue_item_handle)

        assert isinstance(event, GitHubEvent)
        assert event.type == "push"
        payload: PushEvent = event.payload

        async with self.deploy_lock:
            if await persisted_event_exists(event):
                self._logger.warn(f"Ignoring received event {event.id} as it's a duplicate (an event with its ID has already been processed)")
                return

            head_commit_ref = payload["head_commit"]["id"]
            status = github.statuses.CommitStatus(
                f"continuous-integration/{getenv("PYTHON_APP_INSTANCE")}",
                state="pending",
            )
            await github.statuses.create(self.repository_full_name, head_commit_ref, status)
            try:
                await self.on_push(payload)
                await persist_handled_event(event)
            except Exception:
                status.state = "failure"
                await github.statuses.create(self.repository_full_name, head_commit_ref, status)
                raise

            status.state = "success"
            await github.statuses.create(self.repository_full_name, head_commit_ref, status)

    async def on_push(self, payload: PushEvent) -> None:
        pass

    async def checkout(self, ref: str) -> FileTreeDiff:
        await git.fetch(self.config.path, self._logger)
        file_tree_diff = await git.diff(self.config.path, "HEAD", ref)
        await git.checkout(self.config.path, ref, self._logger)
        return file_tree_diff

