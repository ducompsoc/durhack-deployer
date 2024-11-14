import asyncio
import argparse
from argparse import ArgumentTypeError
from typing import Awaitable, Callable, Self

from config import DurHackDeploymentConfig
from deployments import lookup_deployment_by_slug, Deployment
from queue_worker_base import run_worker
from .worker import DurHackQueueWorker


parser = argparse.ArgumentParser(
    prog="durhack-queue-worker",
    description="Handles queued 'push' events from the ducompsoc/durhack repository.",
)


def lookup_durhack_deployment_by_slug(slug: str) -> Deployment[DurHackDeploymentConfig]:
    deployment = lookup_deployment_by_slug(slug)
    if deployment is None:
        raise ArgumentTypeError(f"Deployment '{slug}' could not be found") from KeyError
    if not isinstance(deployment.config, DurHackDeploymentConfig):
        raise ArgumentTypeError(f"Deployment '{slug}' is for {deployment.config.repository}, expected ducompsoc/durhack") from ValueError
    return deployment


parser.add_argument(
    "-d",
    "--deployment",
    "--deployment-slug",
    required=True,
    dest="deployment",
    metavar="slug",
    type=lookup_durhack_deployment_by_slug,
)
subparsers = parser.add_subparsers(required=False)

run_parser = subparsers.add_parser("run")

deploy_parser = subparsers.add_parser("deploy")


class DurHackArgNamespace(argparse.Namespace):
    deployment: Deployment[DurHackDeploymentConfig]
    main: Callable[[Self], Awaitable[None]]


async def run(args: DurHackArgNamespace) -> None:
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(DurHackQueueWorker, args.deployment)


async def deploy(args: DurHackArgNamespace) -> None:
    worker = DurHackQueueWorker(args.deployment)
    await worker.on_init()


parser.set_defaults(main=run)
run_parser.set_defaults(main=run)
deploy_parser.set_defaults(main=deploy)


async def main() -> None:
    args = parser.parse_args(None, DurHackArgNamespace())
    await args.main(args)


if __name__ == '__main__':
    asyncio.run(main())
