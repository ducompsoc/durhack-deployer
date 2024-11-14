import asyncio
from typing import Awaitable, Callable, Self

from config import NginxDeploymentConfig
from queue_worker_base import run_worker
from queue_workers.deployment_worker_arg_parser import make_deployment_worker_argument_parser, DeploymentWorkerArgNamespace
from .worker import NginxQueueWorker

parser = make_deployment_worker_argument_parser(
    prog_name="nginx-queue-worker",
    description="Handles queued 'push' events from the ducompsoc/durhack-nginx repository.",
    deployment_config_type=NginxDeploymentConfig,
    repository_full_name="ducompsoc/durhack-nginx",
)


class NginxArgNamespace(DeploymentWorkerArgNamespace[NginxDeploymentConfig]):
    main: Callable[[Self], Awaitable[None]]


async def run(args: NginxArgNamespace) -> None:
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(NginxQueueWorker, args.deployment, until=args.create_until_future())


async def deploy(args: NginxArgNamespace) -> None:
    worker = NginxQueueWorker(args.deployment)
    await worker.on_init()


parser.top_level_parser.set_defaults(main=run)
parser.run_parser.set_defaults(main=run)
parser.deploy_parser.set_defaults(main=deploy)


async def main() -> None:
    args = parser.top_level_parser.parse_args(None, NginxArgNamespace())
    await args.main(args)


if __name__ == '__main__':
    asyncio.run(main())
