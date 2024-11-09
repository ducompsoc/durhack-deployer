from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess


async def checkout(path: Path, commit_hash: str, logger: Logger | None = None) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"git -C {path} checkout {commit_hash}"
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`git checkout {commit_hash}` exited with status {result.exit_code}; {result.stderr}")
