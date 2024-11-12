import asyncio
from dataclasses import dataclass
import os
from itertools import chain

from config import config


@dataclass
class SubprocessResult:
    exit_code: int
    stdout: str
    stderr: str


def extend_path(env: dict[str, str]) -> None:
    path = env.get("PATH", None)
    if path is None:
        env["PATH"] = ":".join(config.executable_search_paths)
    env["PATH"] = ":".join(chain((path,), config.executable_search_paths))


async def run(cmd: str, env: dict[str, str] | None = None) -> SubprocessResult:
    if env is None:
        env = os.environ.copy()
    extend_path(env)

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout, stderr = await proc.communicate()

    if (code := proc.returncode) is None:
        code = 1

    return SubprocessResult(
        code,
        stdout.decode("utf8", errors="ignore").rstrip(),
        stderr.decode("utf8", errors="ignore").rstrip(),
    )


__all__ = ("run",)
