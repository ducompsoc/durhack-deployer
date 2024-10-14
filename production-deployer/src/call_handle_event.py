from data_types import GitHubEvent
from worker import handle_event


event = GitHubEvent(
    {},
    "pongies",
    "abcdefg"
)
handle_event.delay(event)
