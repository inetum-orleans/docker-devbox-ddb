# -*- coding: utf-8 -*-
import os
import tempfile
from subprocess import run, PIPE
from typing import Union, Iterable, Callable

import yaml

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder


class YttAction(InitializableAction):
    """
    Render ytt files based on filename suffixes.
    """

    def __init__(self):
        super().__init__()
        self.template_finder = None  # type: TemplateFinder

    @property
    def name(self) -> str:
        return "ytt:render"

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return "phase:configure", \
               ("event:file-generated", self.on_file_generated), \
               ("ytt:template-found", self.render_ytt)

    def initialize(self):
        self.template_finder = TemplateFinder(config.data["ytt.includes"],
                                              config.data["ytt.excludes"],
                                              config.data["ytt.suffixes"])

    def execute(self, *args, **kwargs):
        for template, target in self.template_finder.templates:
            bus.emit('ytt:template-found', template=template, target=target)

    def on_file_generated(self, source: str, target: str):  # pylint:disable=unused-argument
        """
        Called when a file is generated.
        """
        template = target
        target = self.template_finder.get_target(template)
        if target:
            self.render_ytt(template, target)

    @staticmethod
    def _escape_config(input_config: dict):
        new = {}
        keywords = config.data["ytt.keywords"]
        keywords_escape_format = config.data["ytt.keywords_escape_format"]
        for key, value in input_config.items():
            if isinstance(value, dict):
                value = YttAction._escape_config(value)
            if key in keywords:
                escaped_k = keywords_escape_format % (key,)
                if escaped_k not in value.keys():
                    new[escaped_k] = value
            new[key] = value
        return new

    def render_ytt(self, template: str, target: str):
        """
        Render a YTT template
        """
        yaml_config = yaml.dump(YttAction._escape_config(config.data.to_dict()))

        includes = TemplateFinder.build_default_includes_from_suffixes(
            config.data["ytt.depends_suffixes"],
            config.data["ytt.extensions"]
        )
        template_finder = TemplateFinder(includes, [], config.data["ytt.depends_suffixes"],
                                         os.path.dirname(target),
                                         recursive=False, skip_processed_targets=False)

        depends_files = [template[0] for template in template_finder.templates]
        if target in depends_files:
            depends_files.remove(target)

        input_files_args = []
        yaml_config_file = tempfile.NamedTemporaryFile("w", suffix=".yml", encoding="utf-8", delete=False)

        try:
            try:
                input_files = [template, yaml_config_file.name] + depends_files
                for input_file in input_files:
                    input_files_args += ["-f", input_file]

                yaml_config_file.write("#@data/values")
                yaml_config_file.write(os.linesep)
                yaml_config_file.write("---")
                yaml_config_file.write(os.linesep)
                yaml_config_file.write(yaml_config)
                yaml_config_file.flush()
            finally:
                yaml_config_file.close()

            rendered = run([config.data["ytt.bin"]] + input_files_args + config.data["ytt.args"],
                           check=True,
                           stdout=PIPE, stderr=PIPE)

            with open(target, "wb") as output_file:
                output_file.write(rendered.stdout)
            self.template_finder.mark_as_processed(template, target)
            bus.emit('event:file-generated', source=template, target=target)
        finally:
            os.unlink(yaml_config_file.name)
