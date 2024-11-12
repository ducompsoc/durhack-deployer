import asyncio
import logging
from contextlib import asynccontextmanager
import signal
from pathlib import Path
from typing import TYPE_CHECKING, Type, Optional

from definitions import project_root_dir

if TYPE_CHECKING:
    from asyncio.subprocess import Process
from logging import Logger, getLogger

from colorlog.escape_codes import escape_codes

from deployments import deployments, Deployment


class SubprocessMessage:
    def __init__(self, message: str, *, subprocess: str):
        self.message = message
        self.subprocess = subprocess

    def __str__(self):
        return f"[{escape_codes.get("fg_purple")}{self.subprocess}{escape_codes.get("reset")}] {self.message}"


class QueueWorkerSupervisor:
    def __init__(
        self,
        deployments: dict[str, Deployment],
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        logger: Logger | None = None
    ):
        self._loop = loop if loop is not None else asyncio.get_running_loop()
        self._logger = logger if logger is not None else getLogger(__name__)
        self.deployments = deployments
        self.main_queue_worker_process: Optional["Process"] = None
        self.deployment_queue_worker_processes: dict[str, "Process"] = dict()

    @property
    def has_running_processes(self) -> bool:
        if self.main_queue_worker_process is not None: return True
        return bool(self.deployment_queue_worker_processes)

    async def dispatch_main_queue_worker(self) -> "Process":
        if self.main_queue_worker_process is not None:
            raise Exception("Refusing to dispatch main queue worker as it is (seemingly) already running")
        self._logger.debug(SubprocessMessage("Dispatching queue worker ...", subprocess="main"))
        process = await asyncio.create_subprocess_shell(
            f"{Path(project_root_dir, ".venv.", "bin", "python")} -m main_queue_worker",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._logger.info(SubprocessMessage(f"Dispatched queue worker has PID {process.pid}", subprocess="main"))

        async def cleanup_on_exit():
            stdout, stderr = await process.communicate()
            exit_code = process.returncode
            if self.main_queue_worker_process is not process:
                return
            self.main_queue_worker_process = None
            self._logger.log(
                logging.WARN if exit_code > 0 else logging.INFO,
                SubprocessMessage(
                    f"Queue worker (PID {process.pid}) has exited with status {exit_code}",
                    subprocess="main",
                ),
            )
            self._logger.debug((SubprocessMessage(f"stdout: {stdout}", subprocess="main")))
            self._logger.debug((SubprocessMessage(f"stderr: {stderr}", subprocess="main")))
        self._loop.create_task(cleanup_on_exit())

        self.main_queue_worker_process = process
        return process

    def create_main_queue_worker_dispatch_task(self, task_group: asyncio.TaskGroup | None = None) -> asyncio.Task["Process"]:
        if task_group is not None:
            return task_group.create_task(self.dispatch_main_queue_worker())
        return self._loop.create_task(self.dispatch_main_queue_worker())

    async def dispatch_deployment_queue_worker(self, deployment: Deployment) -> Optional["Process"]:
        assert self.deployments.get(deployment.slug) is deployment
        if not deployment.config.enabled:
            self._logger.info(SubprocessMessage("Skipping queue worker dispatch as deployment is disabled", subprocess=deployment.slug))
            return None
        if deployment.slug in self.deployment_queue_worker_processes:
            raise Exception(f"Refusing to dispatch queue worker for deployment '{deployment.slug}' as it is (seemingly) already running")
        self._logger.debug(SubprocessMessage("Dispatching queue worker ...", subprocess=deployment.slug))
        process = await asyncio.create_subprocess_shell(
            f"python -m '{deployment.config.worker_module}' -d '{deployment.slug}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._logger.info(SubprocessMessage(f"Dispatched queue worker has PID {process.pid}", subprocess=deployment.slug))

        async def cleanup_on_exit():
            stdout, stderr = await process.communicate()
            exit_code = process.returncode
            if self.deployment_queue_worker_processes.get(deployment.slug) is not process:
                return
            del self.deployment_queue_worker_processes[deployment.slug]

            self._logger.log(
                logging.WARN if exit_code > 0 else logging.INFO,
                SubprocessMessage(
                    f"Queue worker (PID {process.pid}) has exited with status {exit_code}",
                    subprocess=deployment.slug,
                ),
            )
            self._logger.debug((SubprocessMessage(f"stdout: {stdout}", subprocess=deployment.slug)))
            self._logger.debug((SubprocessMessage(f"stderr: {stderr}", subprocess=deployment.slug)))
        self._loop.create_task(cleanup_on_exit())

        self.deployment_queue_worker_processes[deployment.slug] = process
        return process

    def create_deployment_queue_worker_dispatch_task(self, deployment: Deployment, task_group: asyncio.TaskGroup | None = None) -> asyncio.Task[Optional["Process"]]:
        assert self.deployments.get(deployment.slug) is deployment
        if task_group is not None:
            return task_group.create_task(self.dispatch_deployment_queue_worker(deployment))
        return self._loop.create_task(self.dispatch_deployment_queue_worker(deployment))

    async def wait_for_main_queue_worker_process(self) -> int | None:
        if self.main_queue_worker_process is None:
            self._logger.info(SubprocessMessage("queue worker is not running, don't need to wait", subprocess="main"))
            return None
        self._logger.info(SubprocessMessage("Waiting for queue worker to exit ...", subprocess="main"))
        exit_code = await self.main_queue_worker_process.wait()
        return exit_code

    def create_main_queue_worker_process_wait_task(self, task_group: asyncio.TaskGroup | None = None) -> asyncio.Task[int]:
        if task_group is not None:
            return task_group.create_task(self.wait_for_main_queue_worker_process())
        return self._loop.create_task(self.wait_for_main_queue_worker_process())

    async def wait_for_deployment_queue_worker_process(self, deployment: Deployment) -> int | None:
        assert self.deployments.get(deployment.slug) is deployment
        process = self.deployment_queue_worker_processes.get(deployment.slug, None)
        if process is None:
            self._logger.info(SubprocessMessage("Queue worker is not running, don't need to wait", subprocess=deployment.slug))
            return
        self._logger.info(SubprocessMessage("Waiting for queue worker to exit ...", subprocess=deployment.slug))
        exit_code = await process.wait()
        return exit_code

    def create_deployment_queue_worker_process_wait_task(self, deployment: Deployment, task_group: asyncio.TaskGroup | None = None) -> asyncio.Task[int]:
        assert self.deployments.get(deployment.slug) is deployment
        if task_group is not None:
            return task_group.create_task(self.wait_for_deployment_queue_worker_process(deployment))
        return self._loop.create_task(self.wait_for_deployment_queue_worker_process(deployment))

    async def dispatch(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            self.create_main_queue_worker_dispatch_task(task_group)
            for deployment in self.deployments.values():
                self.create_deployment_queue_worker_dispatch_task(deployment, task_group)

    def interrupt(self) -> None:
        if self.main_queue_worker_process is None:
            self._logger.debug(SubprocessMessage("Skipping interrupt, process not found", subprocess="main"))

        if self.main_queue_worker_process is not None:
            self._logger.debug(SubprocessMessage("Sending SIGINT", subprocess="main"))
            self.main_queue_worker_process.send_signal(signal.SIGINT)

        for deployment in self.deployments.values():
            process = self.deployment_queue_worker_processes.get(deployment.slug, None)
            if process is None:
                self._logger.debug(SubprocessMessage("Skipping interrupt, process not found", subprocess=deployment.slug))
                continue

            self._logger.debug(SubprocessMessage("Sending SIGINT", subprocess=deployment.slug))
            process.send_signal(signal.SIGINT)

    async def wait(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            self.create_main_queue_worker_process_wait_task(task_group)
            for deployment in self.deployments.values():
                self.create_deployment_queue_worker_process_wait_task(deployment, task_group)

    @asynccontextmanager
    async def run(self):
        self._logger.info("Supervisor start")
        await self.dispatch()

        try:
            yield None
        finally:
            self._logger.info("Supervisor stop")
            if not self.has_running_processes:
                self._logger.info("No processes to wait for; goodbye")
                return
            self.interrupt()
            await self.wait()
            self._logger.info("goodbye")


async def run_supervisor(supervisor_factory: Type[QueueWorkerSupervisor], *args, **kwargs) -> None:
    loop = asyncio.get_running_loop()
    interrupted = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, interrupted.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, interrupted.set_result, None)

    supervisor = supervisor_factory(*args, **kwargs, loop=loop)
    async with supervisor.run():
        await interrupted


async def main() -> None:
    await run_supervisor(QueueWorkerSupervisor, deployments)


if __name__ == "__main__":
    asyncio.run(main())
