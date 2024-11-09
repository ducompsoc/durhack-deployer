from logging import Logger, getLogger

from util import async_subprocess


async def reload(
    unit_name: str,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"sudo systemctl reload {unit_name}"
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`systemctl reload {unit_name}` exited with status {result.exit_code}; {result.stderr}")
