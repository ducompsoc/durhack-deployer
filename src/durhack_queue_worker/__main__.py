import asyncio
import argparse
from argparse import ArgumentTypeError

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


class DeployerArgNamespace(argparse.Namespace):
    deployment: Deployment[DurHackDeploymentConfig]


async def main() -> None:
    args = parser.parse_args(None, DeployerArgNamespace())
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(DurHackQueueWorker, args.deployment)


if __name__ == '__main__':
    asyncio.run(main())
