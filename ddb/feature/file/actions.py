# -*- coding: utf-8 -*-
import logging
import os

from slugify import slugify
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.utils.delayed_queue import DelayedQueue

from ddb.action import InitializableAction
from ddb.action.action import WatchSupport
from ddb.cache import caches, _project_cache_name, ShelveCache
from ddb.config import config
from ddb.context import context
from ddb.event import bus
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
        return "phase:configure"

    def initialize(self):
        self.file_walker = FileWalker(config.data.get("file.includes"),
                                      config.data.get("file.excludes"),
                                      config.data.get("file.suffixes"))

        caches.register(
            ShelveCache(slugify(_project_cache_name + '.' + config.paths.project_home + ".file",
                                regex_pattern=r'[^-a-z0-9_\.]+')),
            _project_cache_name + ".file")

    def execute(self):
        """
        Execute action
        """
        cache = caches.get(_project_cache_name + ".file")
        found_files = set()

        event_name = "file:found"

        for file in self.file_walker.items:
            cache.set(file, None)
            found_files.add(file)
            bus.emit(event_name, file=file)

        for cached_file in cache.keys():
            if cached_file not in found_files:
                cache.pop(cached_file)
                bus.emit("file:deleted", file=cached_file)

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

    def emit_if_not_filtered(self, event, file):
        """
        Emit given event if file is not filtered by file_walker
        """
        if not file.endswith('~') and not self.action.file_walker.is_source_filtered(file):
            logging.getLogger("ddb.watch").debug("%s", file)
            context.mark_as_unprocessed(file)
            bus.emit(event, file=file)

    def on_modified(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered("file:found", source)

    def on_created(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered("file:found", source)

    def on_deleted(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            self.emit_if_not_filtered("file:deleted", source)

    def on_moved(self, event):
        if not event.is_directory:
            source = os.path.relpath(event.src_path)
            destination = os.path.relpath(event.dest_path)
            self.emit_if_not_filtered("file:found", destination)
            self.emit_if_not_filtered("file:deleted", source)
