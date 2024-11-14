import asyncio
import argparse
from argparse import ArgumentTypeError
from typing import Awaitable, Callable, Self

from config import DurHackDeploymentConfig
from queue_worker_base import run_worker
from queue_workers.deployment_worker_arg_parser import make_deployment_worker_argument_parser, DeploymentWorkerArgNamespace

from .worker import DurHackQueueWorker

parser = make_deployment_worker_argument_parser(
    prog_name="durhack-queue-worker",
    description="Handles queued 'push' events from the ducompsoc/durhack repository.",
    deployment_config_type=DurHackDeploymentConfig,
    repository_full_name="ducompsoc/durhack",
)


class DurHackArgNamespace(DeploymentWorkerArgNamespace[DurHackDeploymentConfig]):
    main: Callable[[Self], Awaitable[None]]


async def run(args: DurHackArgNamespace) -> None:
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(DurHackQueueWorker, args.deployment)


async def deploy(args: DurHackArgNamespace) -> None:
    worker = DurHackQueueWorker(args.deployment)
    await worker.on_init()


parser.top_level_parser.set_defaults(main=run)
parser.run_parser.set_defaults(main=run)
parser.deploy_parser.set_defaults(main=deploy)


async def main() -> None:
    args = parser.top_level_parser.parse_args(None, DurHackArgNamespace())
    await args.main(args)


if __name__ == '__main__':
    asyncio.run(main())
