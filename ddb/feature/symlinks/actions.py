# -*- coding: utf-8 -*-
import os

from ddb.action import InitializableAction
from ddb.action.action import EventBinding
from ddb.config import config
from ddb.context import context
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
    def event_bindings(self):
        def file_found_processor(file: str):
            """
            Called when a file is found.
            """
            source = file
            target = self.template_finder.get_target(source)
            if target:
                return (), {"source": source, "target": target}
            return None

        def file_generated_processor(source: str, target: str):
            """
            Called when a file is generated.
            """
            source = target
            target = self.template_finder.get_target(source)
            if target:
                return (), {"source": source, "target": target}
            return None

        return (EventBinding("file:found", self.create_symlink, file_found_processor), \
                EventBinding("file:generated", self.create_symlink, file_generated_processor))

    def initialize(self):
        self.template_finder = TemplateFinder(config.data.get("symlinks.includes"),
                                              config.data.get("symlinks.excludes"),
                                              config.data.get("symlinks.suffixes"))

    def create_symlink(self, source, target):
        """
        Create a symbolic link
        """
        relsource = os.path.relpath(source, os.path.dirname(target))

        if os.path.islink(target) and os.readlink(target) == relsource:
            context.log.notice("%s -> %s", source, target)
            return

        if os.path.exists(target):
            os.remove(target)

        os.symlink(relsource, os.path.normpath(target))
        context.log.success("%s -> %s", source, target)

        self.template_finder.mark_as_processed(source, target)
        bus.emit('file:generated', source=source, target=target)
