import logging
import os
from collections.abc import Callable
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ddb.action import InitializableAction
from ddb.action.action import EventBindings, WatchSupport
from ddb.cache import caches, register_project_cache
from ddb.config import config
from ddb.context import context
from ddb.event import events
from ddb.utils.file import FileWalker

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver


class FileWalkAction(InitializableAction, WatchSupport):
    """
    Emit events for files inside project matching patterns.
    """

    def __init__(self) -> None:
        super().__init__()
        # Both are set by initialize() and start_watching(), before they are used.
        self.file_walker: FileWalker = None  # type: ignore[assignment]
        self.observer: BaseObserver = None  # type: ignore[assignment]

    @property
    def name(self) -> str:
        return "file:walk"

    @property
    def event_bindings(self) -> EventBindings:
        return events.phase.configure

    def initialize(self) -> None:
        self.file_walker = FileWalker(
            config.data.get("file.includes"),
            config.data.get("file.excludes"),
            config.data.get("file.include_files"),
            config.data.get("file.exclude_files"),
            config.data.get("file.suffixes"),
        )

        register_project_cache("file")

    def destroy(self) -> None:
        if caches.has("file"):
            caches.unregister("file", callback=lambda c: c.close())

    def execute(self) -> None:
        """
        Execute action.
        """
        cache = caches.get("file")
        found_files = set()

        context.log.debug("Walk through all existing files")
        for file in self.file_walker.items:
            cache.set(file, None)
            found_files.add(file)
        context.log.debug("%s files found", len(found_files))

        context.log.debug("Emit events for removed files using cache from previous run")
        for cached_file in cache.keys():
            if cached_file not in found_files:
                cache.pop(cached_file)
                events.file.deleted(cached_file)

        context.log.debug("Generate found events for all actual files")
        for file in self.file_walker.items:
            events.file.found(file)

        cache.flush()

    def start_watching(self) -> None:
        # watchdog ships a py.typed marker but leaves its observer API unannotated.
        self.observer = Observer()
        self.observer.schedule(  # type: ignore[no-untyped-call]
            ObserverHandler(self), str(self.file_walker.rootpath), self.file_walker.recursive
        )
        self.observer.start()  # type: ignore[no-untyped-call]

    def stop_watching(self) -> None:
        self.observer.stop()  # type: ignore[no-untyped-call]

    def join_watching(self) -> None:
        self.observer.join()


class ObserverHandler(FileSystemEventHandler):
    """
    File watcher handler.
    """

    def __init__(self, action: FileWalkAction) -> None:
        self.action = action

    def emit_if_not_filtered(self, func: Callable[..., None], file: str) -> None:
        """
        Emit given event if file is not filtered by file_walker.
        """
        if not file.endswith("~") and not self.action.file_walker.is_source_filtered(file):
            logging.getLogger("ddb.watch").debug("%s", file)
            context.mark_as_unprocessed(file)
            func(file=file)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered(events.file.found, source)

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered(events.file.found, source)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered(events.file.deleted, source)

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            destination = os.path.relpath(event.dest_path)
            self.emit_if_not_filtered(events.file.found, destination)
            self.emit_if_not_filtered(events.file.deleted, source)
