from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess


async def install(
    path: Path,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"uv sync --active --frozen",
        cwd=path,
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`uv sync` exited with status {result.exit_code}; {result.stderr}")
