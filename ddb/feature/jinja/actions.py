# -*- coding: utf-8 -*-
import os

from jinja2 import Environment, FileSystemLoader

from ddb.action import Action
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


class RenderAction(Action):
    """
    Render jinja templates based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "jinja:render"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    def execute(self, *args, **kwargs):
        generator = TemplateFinder(config.data["jinja.includes"],
                                   config.data["jinja.excludes"],
                                   config.data["jinja.suffixes"])

        env = Environment(
            loader=FileSystemLoader(str(generator.rootpath)),
        )

        env.filters.update(custom_filters)
        env.tests.update(custom_tests)

        context = dict(config.data)

        for template, target in generator.templates:
            self._render_template(template, target, env, **context)

    @staticmethod
    def _normpath(path):
        normpath = os.path.normpath(path)
        if os.name == "nt":
            normpath = normpath.replace("\\", "/")
        return normpath

    @staticmethod
    def _render_template(template_path: str, target_path: str, env: Environment, **context):
        template = env.get_template(RenderAction._normpath(template_path))
        template.render(**context)

        with open(target_path, 'w') as target:
            target.write(template.render(**context))
        bus.emit('event:file-generated', source=template_path, target=target_path)
