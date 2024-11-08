import asyncio
import argparse
import logging

from deployments import deployments
from util import configure_console_logging

from .supervisor import run_supervisor, QueueWorkerSupervisor


logger = logging.getLogger("supervisor")
configure_console_logging(logger)
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(
    prog="queue-worker-supervisor",
    description="Dispatches and supervises durhack-deployer queue workers.",
)


async def main() -> None:
    parser.parse_args()
    await run_supervisor(QueueWorkerSupervisor, deployments, logger=logger)


if __name__ == '__main__':
    asyncio.run(main())
