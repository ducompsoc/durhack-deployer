from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess
from shell.pnpm._util import get_filter_options


async def run(
    project_path: Path,
    script: str,
    filter_selector: str | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)
    if cwd is not None:
        raise ValueError("cwd must be None for pnpm commands: https://github.com/ducompsoc/durhack-deployer/issues/12")
    cwd = project_path

    filter_options = get_filter_options(filter_selector)

    result = await async_subprocess.run(
        f"pnpm --dir '{project_path}' {filter_options} run '{script}'",
        env=env,
        cwd=cwd,
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pnpm run '{script}'` exited with status {result.exit_code}; {result.stderr}")
