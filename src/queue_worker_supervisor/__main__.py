import asyncio
import argparse
import logging
import sys

from deployments import deployments

from .supervisor import run_supervisor, QueueWorkerSupervisor


logger = logging.getLogger("supervisor")

parser = argparse.ArgumentParser(
    prog="queue-worker-supervisor",
    description="Dispatches and supervises durhack-deployer queue workers.",
)


async def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parser.parse_args()
    await run_supervisor(QueueWorkerSupervisor, deployments, logger=logger)


if __name__ == '__main__':
    asyncio.run(main())
