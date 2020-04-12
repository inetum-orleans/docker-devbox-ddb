# -*- coding: utf-8 -*-
import os
from typing import Union, Iterable, Callable

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder


class SymlinksAction(InitializableAction):
    """
    Creates symbolic links based on filename suffixes.
    """

    def __init__(self):
        super().__init__()
        self.template_finder = None  # type: TemplateFinder

    @property
    def name(self) -> str:
        return "symlinks:create"

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return ("file:found", self.on_file_found), \
               ("file:generated", self.on_file_generated), \
               ("symlinks:create", self.create_symlink)

    def initialize(self):
        self.template_finder = TemplateFinder(config.data.get("symlinks.includes"),
                                              config.data.get("symlinks.excludes"),
                                              config.data.get("symlinks.suffixes"))

    def on_file_found(self, file: str):
        """
        Called when a file is found.
        """
        source = file
        target = self.template_finder.get_target(source)
        if target:
            bus.emit("symlinks:create", source=source, target=target)

    def on_file_generated(self, source: str, target: str):  # pylint:disable=unused-argument
        """
        Called when a file is generated.
        """
        source = target
        target = self.template_finder.get_target(source)
        if target:
            bus.emit("symlinks:create", source=source, target=target)

    def create_symlink(self, source, target):
        """
        Create a symbolic link
        """
        if os.path.islink(target):
            os.unlink(target)
        if os.path.exists(target):
            os.remove(target)

        relsource = os.path.relpath(source, os.path.dirname(target))
        os.symlink(relsource, os.path.normpath(target))
        self.template_finder.mark_as_processed(source, target)
        bus.emit('file:generated', source=source, target=target)
