from os import getenv
from pathlib import Path
from typing import override

import github
from data_types import GitHubEvent
from github_payload_types import PushEvent
from json_serialization import durhack_deployer_json_load
from queue_worker_base import QueueWorkerBase
from queues import Queue


class GitHubRepositoryQueueWorker(QueueWorkerBase):
    def __init__(self, queue: Queue, repository_full_name: str, *args, **kwargs):
        super().__init__(queue, *args, **kwargs)
        self.repository_full_name = repository_full_name

    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
        with open(queue_item_path) as queue_item_handle:
            event = durhack_deployer_json_load(queue_item_handle)

        assert isinstance(event, GitHubEvent)
        assert event.type == "push"
        payload: PushEvent = event.payload

        head_commit_ref = payload["head_commit"]["id"]
        status = github.statuses.CommitStatus(
            f"continuous-integration/{getenv("PYTHON_APP_INSTANCE")}",
            state="pending",
        )
        await github.statuses.create(self.repository_full_name, head_commit_ref, status)
        try:
            await self.process_github_event(event)
        except:
            status.state = "failed"
            await github.statuses.create(self.repository_full_name, head_commit_ref, status)
            raise

        status.state = "success"
        await github.statuses.create(self.repository_full_name, head_commit_ref, status)

    async def process_github_event(self, event: GitHubEvent) -> None:
        pass
