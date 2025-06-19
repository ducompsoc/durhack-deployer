from logging import Logger, getLogger
from pathlib import Path

from util import async_subprocess
from shell.pnpm._util import ensure_cwd_is_none, get_filter_options


async def install(
    project_path: Path,
    filter_selector: str | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)
    ensure_cwd_is_none(cwd)
    cwd=project_path

    filter_options = get_filter_options(filter_selector)

    result = await async_subprocess.run(
        f"pnpm --dir '{project_path}' {filter_options} install",
        cwd=cwd,
        env=env,
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pnpm install` exited with status {result.exit_code}; {result.stderr}")
