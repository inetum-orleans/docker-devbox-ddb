# -*- coding: utf-8 -*-
import logging
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.utils.delayed_queue import DelayedQueue

from ddb.action import InitializableAction
from ddb.action.action import WatchSupport
from ddb.cache import caches, register_project_cache
from ddb.config import config
from ddb.context import context
from ddb.event import events
from ddb.utils.file import FileWalker


class FileWalkAction(InitializableAction, WatchSupport):
    """
    Emit events for files inside project matching patterns.
    """

    def __init__(self):
        super().__init__()
        self.queue = None  # type: DelayedQueue
        self.file_walker = None  # type: FileWalker
        self.observer = None  # type: Observer

    @property
    def name(self) -> str:
        return "file:walk"

    @property
    def event_bindings(self):
        return events.phase.configure

    def initialize(self):
        self.file_walker = FileWalker(config.data.get("file.includes"),
                                      config.data.get("file.excludes"),
                                      config.data.get("file.suffixes"))

        register_project_cache("file")

    def execute(self):
        """
        Execute action
        """
        cache = caches.get("file")
        found_files = set()

        for file in self.file_walker.items:
            cache.set(file, None)
            found_files.add(file)

        for cached_file in cache.keys():
            if cached_file not in found_files:
                cache.pop(cached_file)
                events.file.deleted(cached_file)

        for file in self.file_walker.items:
            events.file.found(file)

        cache.flush()

    def start_watching(self):
        self.observer = Observer()
        self.observer.schedule(ObserverHandler(self), str(self.file_walker.rootpath), self.file_walker.recursive)
        self.observer.start()

    def stop_watching(self):
        self.observer.stop()

    def join_watching(self):
        self.observer.join()


class ObserverHandler(FileSystemEventHandler):
    """
    File watcher handler
    """

    def __init__(self, action: FileWalkAction):
        self.action = action

    def emit_if_not_filtered(self, func, file):
        """
        Emit given event if file is not filtered by file_walker
        """
        if not file.endswith('~') and not self.action.file_walker.is_source_filtered(file):
            logging.getLogger("ddb.watch").debug("%s", file)
            context.mark_as_unprocessed(file)
            func(file=file)

    def on_modified(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered(events.file.found, source)

    def on_created(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered(events.file.found, source)

    def on_deleted(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered(events.file.deleted, source)

    def on_moved(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            destination = os.path.relpath(event.dest_path)
            self.emit_if_not_filtered(events.file.found, destination)
            self.emit_if_not_filtered(events.file.deleted, source)
