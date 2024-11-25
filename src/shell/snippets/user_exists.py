from logging import Logger, getLogger

from util import async_subprocess


async def user_exists(
    username: str,
    logger: Logger | None = None,
) -> bool:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"id -u ${username}"
    )

    if result.exit_code == 0:
        return True
    if result.exit_code == 1:
        return False

    raise Exception(f"`id` exited with status {result.exit_code}; {result.stderr}")
