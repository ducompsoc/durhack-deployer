import argparse
import signal
from dataclasses import dataclass
from typing import Type

from config import BaseDeploymentConfig
from deployments import Deployment, lookup_deployment_by_slug
from util.async_interrupt import create_interrupt_future


@dataclass
class QueueWorkerArgumentParser:
    top_level_parser: argparse.ArgumentParser

    run_parser: argparse.ArgumentParser
    deploy_parser: argparse.ArgumentParser


def make_deployment_lookup[DeploymentConfig: BaseDeploymentConfig](
    deployment_config_type: Type[DeploymentConfig],
    repository_full_name: str,
):
    def lookup_specific_deployment_by_slug(slug: str) -> Deployment[DeploymentConfig]:
        deployment = lookup_deployment_by_slug(slug)
        if deployment is None:
            raise argparse.ArgumentTypeError(f"Deployment '{slug}' could not be found") from KeyError
        if not isinstance(deployment.config, deployment_config_type):
            raise argparse.ArgumentTypeError(f"Deployment '{slug}' is for {deployment.config.repository}, expected {repository_full_name}") from ValueError
        return deployment

    return lookup_specific_deployment_by_slug


def make_deployment_worker_argument_parser[DeploymentConfig: BaseDeploymentConfig](
    prog_name: str,
    description: str,
    deployment_config_type: Type[DeploymentConfig],
    repository_full_name: str,
):
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description=description,
    )

    parser.add_argument(
        "-d",
        "--deployment",
        "--deployment-slug",
        required=True,
        dest="deployment",
        metavar="slug",
        type=make_deployment_lookup(deployment_config_type, repository_full_name),
    )
    subparsers = parser.add_subparsers(required=False)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument(
        "-s",
        "--supervised",
        dest="supervised",
        action="store_true",
    )

    deploy_parser = subparsers.add_parser("deploy")

    return QueueWorkerArgumentParser(
        top_level_parser=parser,
        run_parser=run_parser,
        deploy_parser=deploy_parser,
    )


class DeploymentWorkerArgNamespace[DeploymentConfig: BaseDeploymentConfig](argparse.Namespace):
    deployment: Deployment[DeploymentConfig]
    supervised: bool

    def create_until_future(self):
        if self.supervised:
            return create_interrupt_future(signals=[signal.SIGTERM])
        return create_interrupt_future(signals=[signal.SIGINT, signal.SIGTERM])
