# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Union, Iterable, Tuple

from ddb.config import config
from ddb.utils.file import TemplateFinder
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from . import filters, tests
from ...action.action import AbstractTemplateAction

custom_filters = vars(filters)
for k in tuple(custom_filters.keys()):
    if k.startswith("__"):
        del custom_filters[k]

custom_tests = vars(tests)
for k in tuple(custom_tests.keys()):
    if k.startswith("__"):
        del custom_tests[k]


class JinjaAction(AbstractTemplateAction):
    """
    Render jinja templates based on filename suffixes.
    """

    def __init__(self):
        super().__init__()
        self.env = None  # type: Environment
        self.context = None  # type: dict

    @property
    def name(self) -> str:
        return "jinja:render"

    def _build_template_finder(self):
        return TemplateFinder(config.data.get("jinja.includes"),
                              config.data.get("jinja.excludes"),
                              config.data.get("jinja.suffixes"))

    def initialize(self):
        super().initialize()

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_finder.rootpath)),
            undefined=StrictUndefined
        )

        self.env.filters.update(custom_filters)
        self.env.tests.update(custom_tests)

        self.context = dict(config.data)

    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        template_name = os.path.relpath(os.path.normpath(template),
                                        os.path.normpath(str(self.template_finder.rootpath)))

        template_name = Path(template_name).as_posix()
        jinja = self.env.get_template(template_name)
        yield jinja.render(**self.context), target
