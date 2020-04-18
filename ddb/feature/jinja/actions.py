# -*- coding: utf-8 -*-
import posixpath

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder, write_if_different
from . import filters, tests
from ...action.action import EventBinding

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
    def event_bindings(self):
        def file_found_processor(file: str):
            template = file
            target = self.template_finder.get_target(template)
            if target:
                return (), {"template": template, "target": target}
            return None

        def file_generated_processor(source: str, target: str):
            template = target
            target = self.template_finder.get_target(template)
            if target:
                return (), {"template": template, "target": target}
            return None

        return (EventBinding("file:found", processor=file_found_processor),
                EventBinding("file:generated", processor=file_generated_processor))

    def initialize(self):
        self.template_finder = TemplateFinder(config.data.get("jinja.includes"),
                                              config.data.get("jinja.excludes"),
                                              config.data.get("jinja.suffixes"))

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_finder.rootpath)),
            undefined=StrictUndefined
        )

        self.env.filters.update(custom_filters)
        self.env.tests.update(custom_tests)

        self.context = dict(config.data)

    def execute(self, template: str, target: str):
        """
        Render jinja template
        """
        template_name = posixpath.relpath(posixpath.normpath(template),
                                          posixpath.normpath(str(self.template_finder.rootpath)))
        jinja = self.env.get_template(template_name)

        written = write_if_different(target, jinja.render(**self.context), 'r', 'w', log_source=template)

        self.template_finder.mark_as_processed(template, target)
        if written:
            bus.emit('file:generated', source=template, target=target)
