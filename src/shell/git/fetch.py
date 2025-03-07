from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess

from ._set_env import set_env


async def fetch(path: Path, logger: Logger | None = None) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"git -C {path} fetch",
        set_env(),
    )

    if result.exit_code == 0:
        return

    if "Permission denied" in result.stderr or "fatal: could not read Password" in result.stderr:
        raise Exception(f"`git fetch` exited with status {result.exit_code}; credentials needed for {path.name}: {result.stderr}")

    raise Exception(f"`git fetch` exited with status {result.exit_code}; {result.stderr}")
