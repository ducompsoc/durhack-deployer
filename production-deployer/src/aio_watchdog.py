import asyncio
from typing import override
from pathlib import Path
from os import PathLike

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

"""
The contents fo this file are loosely based upon hachiko, Copyright (c) 2023 John Biesnecker
https://github.com/biesnecker/hachiko/blob/ad1ca33beaa705ffcf0972877e17f6155b33b963/hachiko/hachiko.py
John Biesnecker licenses hachiko to DU Computing Society under the terms of the MIT license.
DU Computing Society licenses this file to you under the terms of the LGPL-3.0-or-later license.

For example usage, see https://github.com/biesnecker/hachiko/blob/ad1ca33beaa705ffcf0972877e17f6155b33b963/README.md
"""


class AIOEventHandler(FileSystemEventHandler):
    def __init__(self, loop: asyncio.EventLoop | None = None):
        super()
        self._loop = loop if loop is not None else asyncio.get_event_loop()

    @override
    def dispatch(self, event: FileSystemEvent) -> None:
        self._loop.call_soon_threadsafe(asyncio.create_task, self.on_any_event(event))
        self._loop.call_soon_threadsafe(asyncio.create_task, getattr(self, f"on_{event.event_type}"))


class AIOWatchdog:
    def __init__(
        self,
        path: str | PathLike,
        recursive: bool = True,
        event_handler: AIOEventHandler | None = None,
        observer: Observer | None = None,
    ):
        self._observer = observer if observer is not None else Observer()
        self._path = path if isinstance(path, Path) else Path(path)
        event_handler = event_handler or AIOEventHandler()
        self._observer.schedule(event_handler, str(self._path), recursive)

    def start(self) -> None:
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
