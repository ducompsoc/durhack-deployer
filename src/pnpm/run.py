from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess

async def run(project_path: Path, script: str, filter_selector: str | None = None, logger: Logger | None = None) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    filter_option = "" if filter_selector is None else f"--filter '{filter_selector}'"

    result = await async_subprocess.run(
        f"pnpm -C '{project_path}' {filter_option} run '{script}'",
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pnpm run '{script}'` exited with status {result.exit_code}; {result.stderr}")
