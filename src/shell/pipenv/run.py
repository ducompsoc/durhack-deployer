from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess


async def run(
    path: Path,
    script: str,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"pipenv run '{script}'",
        cwd=path,
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pipenv run '{script}'` exited with status {result.exit_code}; {result.stderr}")
