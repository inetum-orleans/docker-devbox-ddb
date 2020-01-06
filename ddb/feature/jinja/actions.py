# -*- coding: utf-8 -*-
import os

from jinja2 import Environment, FileSystemLoader

from ddb.action import Action
from ddb.config import config
from ddb.utils.file import TemplateFinder


class RenderAction(Action):
    """
    Creates symbolic links based on filename suffixes.
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
            loader=FileSystemLoader(str(generator.rootpath))
        )

        context = dict(config.data)

        for template, target in generator.templates:
            self._render_template(template, target, env, **context)

    @staticmethod
    def _render_template(template_path: str, target_path: str, env: Environment, **context):
        template = env.get_template(os.path.normpath(template_path))
        template.render(**context)

        with open(target_path, 'w') as target:
            target.write(template.render(**context))
