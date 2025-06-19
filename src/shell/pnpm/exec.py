from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess


async def exec(
    project_path: Path,
    command: str,
    filter_selector: str | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)
    if cwd is not None:
        raise ValueError("cwd must be None for pnpm commands: https://github.com/ducompsoc/durhack-deployer/issues/12")
    cwd = project_path

    filter_option = "" if filter_selector is None else f"--filter '{filter_selector}'"

    result = await async_subprocess.run(
        f"pnpm {filter_option} exec {command}",
        cwd=cwd,
        env=env,
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pnpm exec {command}` exited with status {result.exit_code}; {result.stderr}")
