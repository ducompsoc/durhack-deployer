from billiard.einfo import ExceptionInfo
from celery import Celery, Task as CeleryTask

from config import config
from data_types import GitHubEvent
from json_serialization import durhack_deployer_json_kombu_serializer_name

app = Celery('worker', broker=str(config.celery_task_broker_uri))
app.conf.task_serializer = durhack_deployer_json_kombu_serializer_name
app.conf.accept_content = ['application/json', 'application/vnd.durhack-deployer+json']


class DurHackDeployerTaskBase(CeleryTask):
    def on_failure(self, exc: BaseException, task_id: str, args: list[object], kwargs: dict[str, object], exc_info: ExceptionInfo=None):
        traceback = (exc_info and exc_info.traceback) or "[no traceback available]"
        print(f'Task {task_id!r} raised exception: {exc!r}\n{traceback!r}')


@app.task(base=DurHackDeployerTaskBase, ignore_result=True)
def _handle_event(event: GitHubEvent) -> None:
    with open(f"{event.type}.txt", "w") as fooHandle:
        fooHandle.write("hello, world")


handle_event: DurHackDeployerTaskBase = _handle_event
