import asyncio
import argparse
from argparse import ArgumentTypeError
from typing import Awaitable, Callable, Self

from config import NginxDeploymentConfig
from deployments import lookup_deployment_by_slug, Deployment
from queue_worker_base import run_worker
from .worker import NginxQueueWorker


parser = argparse.ArgumentParser(
    prog="nginx-queue-worker",
    description="Handles queued 'push' events from the ducompsoc/durhack-nginx repository.",
)


def lookup_nginx_deployment_by_slug(slug: str) -> Deployment[NginxDeploymentConfig]:
    deployment = lookup_deployment_by_slug(slug)
    if deployment is None:
        raise ArgumentTypeError(f"Deployment '{slug}' could not be found") from KeyError
    if not isinstance(deployment.config, NginxDeploymentConfig):
        raise ArgumentTypeError(f"Deployment '{slug}' is for {deployment.config.repository}, expected ducompsoc/durhack-nginx") from ValueError
    return deployment


parser.add_argument(
    "-d",
    "--deployment",
    "--deployment-slug",
    required=True,
    dest="deployment",
    metavar="slug",
    type=lookup_nginx_deployment_by_slug,
)
subparsers = parser.add_subparsers(required=False)

run_parser = subparsers.add_parser("run")

deploy_parser = subparsers.add_parser("deploy")


class NginxArgNamespace(argparse.Namespace):
    deployment: Deployment[NginxDeploymentConfig]
    main: Callable[[Self], Awaitable[None]]


async def run(args: NginxArgNamespace) -> None:
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(NginxQueueWorker, args.deployment)


async def deploy(args: NginxArgNamespace) -> None:
    worker = NginxQueueWorker(args.deployment)
    await worker.on_init()


parser.set_defaults(main=run)
run_parser.set_defaults(main=run)
deploy_parser.set_defaults(main=deploy)


async def main() -> None:
    args = parser.parse_args(None, NginxArgNamespace())
    await args.main(args)


if __name__ == '__main__':
    asyncio.run(main())
