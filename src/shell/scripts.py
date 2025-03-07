from logging import Logger, getLogger
from pathlib import Path
from typing import Awaitable, Callable, Protocol

from definitions import project_root_dir
from util import async_subprocess


class ScriptCallable[**P](Protocol):
    async def __call__(
        self,
        *args: P.args,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        logger: Logger | None = None,
        **kwargs: P.kwargs,
    ) -> None: ...


def script_callable[**P](command_provider: Callable[P, Awaitable[str]]) -> ScriptCallable[P]:
    async def run_script(
        *args,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        logger: Logger | None = None,
        **kwargs,
    ) -> None:
        logger = logger if logger is not None else getLogger(__name__)

        command = await command_provider(*args, **kwargs)

        result = await async_subprocess.run(
            command,
            env=env,
            cwd=cwd,
        )

        if result.exit_code <= 0:
            return

        raise Exception(f"`{command}` exited with status {result.exit_code}; {result.stderr}")

    return run_script


def script_path(script_name: str) -> Path:
    return Path(project_root_dir, "scripts", script_name)


@script_callable
async def add_deployment_user(username: str) -> str:
    return f"'{script_path("add-deployment-user.sh")}' '{username}'"


@script_callable
async def deployment_user_self_setup(username: str) -> str:
    return f"systemd-run --wait --collect --user --machine='{username}'@ bash '{script_path("deployment-user-self-setup.sh")}'"


@script_callable
async def migrate() -> str:
    return f"'{script_path("migrate.sh")}'"
