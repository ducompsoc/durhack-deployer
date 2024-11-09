import asyncio
from dataclasses import dataclass
import functools
import os


@dataclass
class SubprocessResult:
    exit_code: int
    stdout: str
    stderr: str


@functools.cache
def set_env() -> dict:
    """
    GIT_TERMINAL_PROMPT=0 disallows spurious Git https password prompts
    https://github.blog/2015-02-06-git-2-3-has-been-released/#the-credential-subsystem-is-now-friendlier-to-scripting
    """

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


async def run(cmd: str) -> SubprocessResult:
    env = set_env()

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
