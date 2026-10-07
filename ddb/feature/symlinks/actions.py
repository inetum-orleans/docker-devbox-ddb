import os
from collections.abc import Iterable
from pathlib import Path

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
        return TemplateFinder(
            [],
            [],
            config.data.get("symlinks.includes"),
            config.data.get("symlinks.excludes"),
            config.data.get("symlinks.suffixes"),
        )

    def _render_template(self, template: str, target: str) -> Iterable[tuple[str | bytes | bool, str]]:
        """
        Create a symbolic link.
        """
        reltemplate = os.path.relpath(template, Path(target).parent)

        if Path(target).is_symlink() and str(Path(target).readlink()) == reltemplate:
            context.log.notice("%s -> %s", template, target)
            yield False, target
        else:
            if Path(target).exists():
                force_remove(target)

            Path(os.path.normpath(target)).symlink_to(reltemplate)
            context.log.success("%s -> %s", template, target)

            yield True, target

    def _target_is_modified(self, template: str, target: str) -> bool:
        if not Path(target).is_symlink():
            return True
        reltemplate = os.path.relpath(template, Path(target).parent)
        return str(Path(target).readlink()) != reltemplate
