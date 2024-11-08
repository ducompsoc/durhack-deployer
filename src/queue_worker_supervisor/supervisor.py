import asyncio
from contextlib import asynccontextmanager
import signal
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from asyncio.subprocess import Process

from deployments import deployments, Deployment


class QueueWorkerSupervisor:
    def __init__(
        self,
        deployments: dict[str, Deployment],
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        self._loop = loop if loop is not None else asyncio.get_running_loop()
        self.deployments = deployments
        self.main_queue_worker_process: "Process" | None = None
        self.deployment_queue_worker_processes: dict[str, "Process"] = dict()

    async def dispatch_main_queue_worker(self) -> "Process":
        if self.main_queue_worker_process is not None:
            raise Exception("Refusing to dispatch main queue worker as it is (seemingly) already running")
        print("[main] Dispatching queue worker ...")
        process = await asyncio.create_subprocess_shell(
            "python -m main_queue_worker"
        )
        print(f"[main] Dispatched queue worker has PID {process.pid}")

        async def cleanup_on_exit():
            exit_code = await process.wait()
            if self.main_queue_worker_process is not process:
                return
            self.main_queue_worker_process = None
            print(f"[main] Queue worker (PID {process.pid}) has exited with status {exit_code}")
        self._loop.create_task(cleanup_on_exit())

        self.main_queue_worker_process = process
        return process

    def create_main_queue_worker_dispatch_task(self, task_group: asyncio.TaskGroup | None = None) -> asyncio.Task["Process"]:
        if task_group is not None:
            return task_group.create_task(self.dispatch_main_queue_worker())
        return self._loop.create_task(self.dispatch_main_queue_worker())

    async def dispatch_deployment_queue_worker(self, deployment: Deployment) -> "Process":
        assert self.deployments.get(deployment.slug) is deployment
        if deployment.slug in self.deployment_queue_worker_processes:
            raise Exception(f"Refusing to dispatch queue worker for deployment '{deployment.slug}' as it is (seemingly) already running")
        print(f"[{deployment.slug}] Dispatching queue worker ...")
        process = await asyncio.create_subprocess_shell(
            f"python -m '{deployment.config.worker_module}' -d '{deployment.slug}'"
        )
        print(f"[{deployment.slug}] Dispatched queue worker has PID {process.pid}")

        async def cleanup_on_exit():
            exit_code = await process.wait()
            if self.deployment_queue_worker_processes.get(deployment.slug) is not process:
                return
            del self.deployment_queue_worker_processes[deployment.slug]
            print(f"[{deployment.slug}] Queue worker (PID {process.pid}) has exited with status {exit_code}")
        self._loop.create_task(cleanup_on_exit())

        self.deployment_queue_worker_processes[deployment.slug] = process
        return process

    def create_deployment_queue_worker_dispatch_task(self, deployment: Deployment, task_group: asyncio.TaskGroup | None = None) -> asyncio.Task["Process"]:
        assert self.deployments.get(deployment.slug) is deployment
        if task_group is not None:
            return task_group.create_task(self.dispatch_deployment_queue_worker(deployment))
        return self._loop.create_task(self.dispatch_deployment_queue_worker(deployment))

    async def wait_for_main_queue_worker_process(self) -> int | None:
        if self.main_queue_worker_process is None:
            print(f"[main] queue worker is not running, no waiting required")
            return None
        print(f"[main] Waiting for queue worker to exit ...")
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
            print(f"[{deployment.slug}] queue worker is not running, no waiting required")
            return
        print(f"[{deployment.slug}] Waiting for queue worker to exit ...")
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
        if self.main_queue_worker_process is not None:
            print(f"[main] Sending SIGINT")
            self.main_queue_worker_process.send_signal(signal.SIGINT)

        for deployment in self.deployments.values():
            process = self.deployment_queue_worker_processes.get(deployment.slug, None)
            if process is None:
                print(f"[{deployment.slug}] Skipping interrupt, process not found")
                continue

            print(f"[{deployment.slug}] Sending SIGINT")
            process.send_signal(signal.SIGINT)

    async def wait(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            self.create_main_queue_worker_process_wait_task(task_group)
            for deployment in self.deployments.values():
                self.create_deployment_queue_worker_process_wait_task(deployment, task_group)

    @asynccontextmanager
    async def run(self):
        await self.dispatch()

        try:
            yield None
        finally:
            if not self.deployment_queue_worker_processes:
                return
            self.interrupt()
            await self.wait()


async def run_supervisor(supervisor_factory: Type[QueueWorkerSupervisor], *args, **kwargs) -> None:
    loop = asyncio.get_running_loop()
    interrupted = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, interrupted.set_result, None)

    supervisor = supervisor_factory(*args, **kwargs, loop=loop)
    async with supervisor.run():
        await interrupted


async def main() -> None:
    await run_supervisor(QueueWorkerSupervisor, deployments)


if __name__ == "__main__":
    asyncio.run(main())
