import asyncio
from typing import Callable, Self, Awaitable

from queue_workers.deployment_worker_arg_parser import make_deployment_worker_argument_parser, DeploymentWorkerArgNamespace

from config import DeployerDeploymentConfig
from queue_worker_base import run_worker
from .worker import DeployerQueueWorker

parser = make_deployment_worker_argument_parser(
    prog_name="deployer-queue-worker",
    description="Handles queued 'push' events from the ducompsoc/durhack-deployer repository.",
    deployment_config_type=DeployerDeploymentConfig,
    repository_full_name="ducompsoc/durhack-deployer",
)


class DeployerArgNamespace(DeploymentWorkerArgNamespace[DeployerDeploymentConfig]):
    main: Callable[[Self], Awaitable[None]]


async def run(args: DeployerArgNamespace) -> None:
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(DeployerQueueWorker, args.deployment)


async def deploy(args: DeployerArgNamespace) -> None:
    worker = DeployerQueueWorker(args.deployment)
    await worker.on_init()


parser.top_level_parser.set_defaults(main=run)
parser.run_parser.set_defaults(main=run)
parser.deploy_parser.set_defaults(main=deploy)


async def main() -> None:
    args = parser.top_level_parser.parse_args(None, DeployerArgNamespace())
    await args.main(args)


if __name__ == '__main__':
    asyncio.run(main())
