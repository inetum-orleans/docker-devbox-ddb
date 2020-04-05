# -*- coding: utf-8 -*-
import os
from typing import Union, Iterable, Callable

from jinja2 import Environment, FileSystemLoader

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder
from . import filters, tests

custom_filters = vars(filters)
for k in tuple(custom_filters.keys()):
    if k.startswith("__"):
        del custom_filters[k]

custom_tests = vars(tests)
for k in tuple(custom_tests.keys()):
    if k.startswith("__"):
        del custom_tests[k]


class JinjaAction(InitializableAction):
    """
    Render jinja templates based on filename suffixes.
    """
    def __init__(self):
        super().__init__()
        self.template_finder = None  # type: TemplateFinder
        self.env = None  # type: Environment
        self.context = None  # type: dict

    @property
    def name(self) -> str:
        return "jinja:render"

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return "phase:configure", \
               ("event:file-generated", self.on_file_generated), \
               ("jinja:template-found", self.render_jinja)

    def initialize(self):
        self.template_finder = TemplateFinder(config.data["jinja.includes"],
                                              config.data["jinja.excludes"],
                                              config.data["jinja.suffixes"])

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_finder.rootpath)),
        )

        self.env.filters.update(custom_filters)
        self.env.tests.update(custom_tests)

        self.context = dict(config.data)

    def execute(self, *args, **kwargs):
        for template, target in self.template_finder.templates:
            bus.emit("jinja:template-found", template=template, target=target)

    def on_file_generated(self, source: str, target: str):  # pylint:disable=unused-argument
        """
        Called when a file is generated.
        """
        template = target
        target = self.template_finder.get_target(template)
        if target:
            self.render_jinja(template, target)

    @staticmethod
    def _normpath(path):
        normpath = os.path.normpath(path)
        if os.name == "nt":
            normpath = normpath.replace("\\", "/")
        return normpath

    def render_jinja(self, template: str, target: str):
        """
        Render jinja template
        """
        jinja = self.env.get_template(JinjaAction._normpath(template))

        with open(target, 'w') as target_file:
            target_file.write(jinja.render(**self.context))
        self.template_finder.mark_as_processed(template, target)
        bus.emit('event:file-generated', source=template, target=target)
