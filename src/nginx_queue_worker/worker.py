import asyncio
from pathlib import Path
from typing import override

from config import NginxDeploymentConfig, IncludeRule
from deployments import Deployment
from queue_worker_base import QueueWorkerBase, run_worker


class NginxQueueWorker(QueueWorkerBase):
    def __init__(self, deployment: Deployment[NginxDeploymentConfig], *args, **kwargs):
        super().__init__(deployment.queue, *args, **kwargs)

    @override
    async def process_queue_item(self, queue_item_path: Path) -> None:
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