import asyncio
import argparse

from deployments import deployments

from .supervisor import run_supervisor, QueueWorkerSupervisor

parser = argparse.ArgumentParser(
    prog="queue-worker-supervisor",
    description="Dispatches and supervises durhack-deployer queue workers.",
)


async def main() -> None:
    parser.parse_args()
    await run_supervisor(QueueWorkerSupervisor, deployments)


if __name__ == '__main__':
    asyncio.run(main())
