from logging import Logger, getLogger

from util import async_subprocess

async def save(logger: Logger | None = None) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"pm2 save",
    )

    if result.exit_code <= 0:
        return

    raise Exception(f"`pm2 save` exited with status {result.exit_code}; {result.stderr}")
