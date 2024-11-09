import asyncio
from pathlib import Path
from typing import override

from config import NginxDeploymentConfig, IncludeRule
from data_types import GitHubEvent
from deployments import Deployment
from github_payload_types import PushEvent
from json_serialization import durhack_deployer_json_load
from queue_worker_base import QueueWorkerBase, run_worker
from util.aggregate_commit_files import aggregate_commit_files


class NginxQueueWorker(QueueWorkerBase):
    def __init__(self, deployment: Deployment[NginxDeploymentConfig], *args, **kwargs):
        super().__init__(deployment.queue, *args, **kwargs)
        self.deploy_lock = asyncio.Lock()

    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
        with open(queue_item_path) as queue_item_handle:
            event = durhack_deployer_json_load(queue_item_handle)

        assert isinstance(event, GitHubEvent)
        assert event.type == "push"

        payload: PushEvent = event.payload
        file_tree_diff = aggregate_commit_files(payload["commits"])

        async with self.deploy_lock:
            pass


async def main() -> None:
    deployment = Deployment("nginx", NginxDeploymentConfig(
        repository = "ducompsoc/durhack-nginx",
        enabled = True,
        branch = "main",
        path = "/home/joeclack/repos/barbaz",
        sites = [ IncludeRule(rule="include", select=["*"]) ],
    ))
    deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(NginxQueueWorker, deployment)


if __name__ == "__main__":
    asyncio.run(main())
