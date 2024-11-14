from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess

async def reload(config_file: Path, logger: Logger | None = None) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"touch '{config_file}' --no-dereference",
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`touch '{config_file}'` exited with status {result.exit_code}; {result.stderr}")
