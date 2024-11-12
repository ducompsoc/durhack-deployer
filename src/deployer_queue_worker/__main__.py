import asyncio
import argparse
from argparse import ArgumentTypeError

from config import DeployerDeploymentConfig
from deployments import lookup_deployment_by_slug, Deployment
from queue_worker_base import run_worker
from .worker import DeployerQueueWorker


parser = argparse.ArgumentParser(
    prog="deployer-queue-worker",
    description="Handles queued 'push' events from the ducompsoc/durhack-deployer repository.",
)

def lookup_deployer_deployment_by_slug(slug: str) -> Deployment[DeployerDeploymentConfig]:
    deployment = lookup_deployment_by_slug(slug)
    if deployment is None:
        raise ArgumentTypeError(f"Deployment '{slug}' could not be found") from KeyError
    if not isinstance(deployment.config, DeployerDeploymentConfig):
        raise ArgumentTypeError(f"Deployment '{slug}' is for {deployment.config.repository}, expected ducompsoc/durhack-deployer") from ValueError
    return deployment


parser.add_argument(
    "-d",
    "--deployment",
    "--deployment-slug",
    required=True,
    dest="deployment",
    metavar="slug",
    type=lookup_deployer_deployment_by_slug,
)


class DeployerArgNamespace(argparse.Namespace):
    deployment: Deployment[DeployerDeploymentConfig]


async def main() -> None:
    args = parser.parse_args(None, DeployerArgNamespace())
    args.deployment.queue.path.mkdir(parents=True, exist_ok=True)
    await run_worker(DeployerQueueWorker, args.deployment)


if __name__ == '__main__':
    asyncio.run(main())
