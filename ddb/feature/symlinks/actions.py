# -*- coding: utf-8 -*-
import os
from typing import Union, Iterable, Tuple

from ddb.action.action import AbstractTemplateAction
from ddb.config import config
from ddb.context import context
from ddb.utils.file import TemplateFinder, force_remove


class SymlinksAction(AbstractTemplateAction):
    """
    Creates symbolic links based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "symlinks:create"

    def _build_template_finder(self) -> TemplateFinder:
        return TemplateFinder(config.data.get("symlinks.includes"),
                              config.data.get("symlinks.excludes"),
                              config.data.get("symlinks.suffixes"))

    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        """
        Create a symbolic link
        """
        reltemplate = os.path.relpath(template, os.path.dirname(target))

        if os.path.islink(target) and os.readlink(target) == reltemplate:
            context.log.notice("%s -> %s", template, target)
            yield False, target
        else:
            if os.path.exists(target):
                force_remove(target)

            os.symlink(reltemplate, os.path.normpath(target))
            context.log.success("%s -> %s", template, target)

            yield True, target

    def _target_is_modified(self, template: str, target: str) -> bool:
        if not os.path.islink(target):
            return True
        reltemplate = os.path.relpath(template, os.path.dirname(target))
        return os.readlink(target) != reltemplate
