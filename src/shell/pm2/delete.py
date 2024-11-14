from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess


async def delete(
    target: str,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"pm2 del '{target}'",
        env=env,
        cwd=cwd,
    )

    if result.exit_code <= 0:
        return

    if "not found" in result.stdout:  # pm2 logs errors to stdout
        return

    raise Exception(f"`pm2 del '{target}'` exited with status {result.exit_code}; {result.stderr}")
