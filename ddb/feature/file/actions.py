# -*- coding: utf-8 -*-
from typing import Union, Iterable, Callable

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import FileWalker


class FileWalkAction(InitializableAction):
    """
    Emit events for files inside project matching patterns.
    """

    def __init__(self):
        super().__init__()
        self.file_walker = None  # type: FileWalker

    @property
    def name(self) -> str:
        return "file:walk"

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
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
