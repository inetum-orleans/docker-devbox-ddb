# -*- coding: utf-8 -*-
import logging
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.utils.delayed_queue import DelayedQueue

from ddb.action import InitializableAction
from ddb.action.action import WatchSupport
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import FileWalker, TemplateFinder


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

    def execute(self):
        """
        Execute action
        """
        for file in self.file_walker.items:
            bus.emit("file:found", file=file)

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
            TemplateFinder.mark_as_unprocessed(file)
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
            self.emit_if_not_filtered("file:deleted", source)
            self.emit_if_not_filtered("file:found", destination)
