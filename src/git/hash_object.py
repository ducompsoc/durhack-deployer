from logging import Logger, getLogger
from pathlib import Path
from typing import Literal

from util import async_subprocess
from ._set_env import set_env


async def hash_object(
    path: Path,
    file: Path,

    object_type: Literal["commit", "tree", "blob", "tag"] | None = None,
    logger: Logger | None = None,
) -> str:
    logger = logger if logger is not None else getLogger(__name__)

    object_type_arg = "" if object_type is None else f"-t '{object_type}'"

    result = await async_subprocess.run(
        f"git -C {path} hash-object {object_type_arg} -- {file}",
        set_env(),
    )

    if result.exit_code != 0:
        raise Exception(f"`git hash-object` exited with status {result.exit_code}; {result.stderr}")

    return result.stdout.strip()
