# -*- coding: utf-8 -*-
import os

from ddb.action import Action
from ddb.config import config
from ddb.utils.file import TemplateFinder


class CreateAction(Action):
    """
    Creates symbolic links based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "symlinks:create"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    def execute(self, *args, **kwargs):
        template_finder = TemplateFinder(config.data["symlinks.includes"],
                                         config.data["symlinks.excludes"],
                                         config.data["symlinks.suffixes"])

        for source, target in template_finder.templates:
            if os.path.islink(target):
                os.unlink(target)
            if os.path.exists(target):
                os.remove(target)

            relsource = os.path.relpath(source, os.path.dirname(target))
            os.symlink(relsource, os.path.normpath(target))
