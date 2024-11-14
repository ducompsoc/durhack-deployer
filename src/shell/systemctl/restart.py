from logging import Logger, getLogger

from util import async_subprocess


async def restart(
    unit_name: str,
    block: bool = True,
    logger: Logger | None = None,
) -> None:
    logger = logger if logger is not None else getLogger(__name__)

    result = await async_subprocess.run(
        f"sudo systemctl restart {unit_name} {"" if block else "--no-block"}"
    )

    if result.exit_code == 0:
        return

    raise Exception(f"`systemctl restart {unit_name}` exited with status {result.exit_code}; {result.stderr}")
