# -*- coding: utf-8 -*-
import os
from typing import Union, Iterable

from ddb.action import Action
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder


class SymlinkAction(Action):
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
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], str]]]:
        return "phase:configure"

    def initialize(self):
        self.template_finder = TemplateFinder(config.data["symlinks.includes"],
                                              config.data["symlinks.excludes"],
                                              config.data["symlinks.suffixes"])

    def execute(self, *args, **kwargs):
        for source, target in self.template_finder.templates:
            if os.path.islink(target):
                os.unlink(target)
            if os.path.exists(target):
                os.remove(target)

            relsource = os.path.relpath(source, os.path.dirname(target))
            os.symlink(relsource, os.path.normpath(target))
            bus.emit('event:file-generated', source=source, target=target)
