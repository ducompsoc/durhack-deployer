import os
from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess

async def reload(instance_name: str, ecosystem_file: Path, logger: Logger | None = None) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    env = os.environ.copy()
    env["INSTANCE_NAME"] = instance_name

    result = await async_subprocess.run(
        f"pm2 reload '{ecosystem_file}'",
        env,
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`pm2 reload '{ecosystem_file}'` exited with status {result.exit_code}; {result.stderr}")
