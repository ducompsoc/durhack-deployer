from dataclasses import dataclass
from pathlib import Path
from time import time_ns

from definitions import project_root_dir
from json_serialization import durhack_deployer_json_dump

queue_directory = Path(project_root_dir, "queues")


@dataclass
class Queue:
    slug: str

    @property
    def path(self):
        return Path(queue_directory, self.slug)

    def push_event(self, event: object) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        event_item_filepath = Path(self.path, f"${time_ns()}.json")
        with open(event_item_filepath, "x") as event_item_handle:
            durhack_deployer_json_dump(event, event_item_handle)


main_queue = Queue("main")
base_queue = Queue("base")
