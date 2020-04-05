# -*- coding: utf-8 -*-
import os
from typing import Union, Iterable, Callable

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder


class SymlinkAction(InitializableAction):
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
        return "phase:configure", ("event:file-generated", self.on_file_generated)

    def initialize(self):
        self.template_finder = TemplateFinder(config.data["symlinks.includes"],
                                              config.data["symlinks.excludes"],
                                              config.data["symlinks.suffixes"])

    def on_file_generated(self, source: str, target: str):  # pylint:disable=unused-argument
        """
        Called when a file is generated.
        """
        template = target
        target = self.template_finder.get_target(template)
        if target:
            self._create_symlink(template, target)

    def execute(self, *args, **kwargs):
        for source, target in self.template_finder.templates:
            self._create_symlink(source, target)

    def _create_symlink(self, source, target):
        if os.path.islink(target):
            os.unlink(target)
        if os.path.exists(target):
            os.remove(target)

        relsource = os.path.relpath(source, os.path.dirname(target))
        os.symlink(relsource, os.path.normpath(target))
        self.template_finder.mark_as_processed(source, target)
        bus.emit('event:file-generated', source=source, target=target)
