from logging import Logger, getLogger

from util import async_subprocess


async def restart(
    target: str,
    env: dict[str, str] | None = None,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"pm2 restart '{target}'",
        env,
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pm2 restart '{target}'` exited with status {result.exit_code}; {result.stderr}")
