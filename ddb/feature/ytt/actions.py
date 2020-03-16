# -*- coding: utf-8 -*-
import os
import tempfile
from subprocess import run, PIPE

import yaml

from ddb.action import Action
from ddb.config import config
from ddb.utils.file import TemplateFinder


class RenderAction(Action):
    """
    Render ytt files based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "ytt:render"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    def execute(self, *args, **kwargs):
        generator = TemplateFinder(config.data["ytt.includes"],
                                   config.data["ytt.excludes"],
                                   config.data["ytt.suffixes"])

        for template, target in generator.templates:
            self._render_ytt(template, target)

    @staticmethod
    def _escape_config(input_config: dict):
        new = {}
        keywords = config.data["ytt.keywords"]
        keywords_escape_format = config.data["ytt.keywords_escape_format"]
        for key, value in input_config.items():
            if isinstance(value, dict):
                value = RenderAction._escape_config(value)
            if key in keywords:
                escaped_k = keywords_escape_format % (key,)
                if escaped_k not in value.keys():
                    new[escaped_k] = value
            new[key] = value
        return new

    @staticmethod
    def _render_ytt(template_path: str, target_path: str):
        yaml_config = yaml.dump(RenderAction._escape_config(config.data.to_dict()))

        includes = TemplateFinder.build_default_includes_from_suffixes(
            config.data["ytt.depends_suffixes"],
            config.data["ytt.extensions"]
        )
        template_finder = TemplateFinder(includes, [], config.data["ytt.depends_suffixes"],
                                         os.path.dirname(target_path),
                                         recursive=False, first_only=False)

        depends_files = [template[0] for template in template_finder.templates]
        if target_path in depends_files:
            depends_files.remove(target_path)

        yaml_config_file = tempfile.NamedTemporaryFile("w", suffix=".yml", encoding="utf-8")

        input_files = [template_path, yaml_config_file.name] + depends_files
        input_files_args = []
        for input_file in input_files:
            input_files_args += ["-f", input_file]

        try:
            yaml_config_file.write("#@data/values")
            yaml_config_file.write(os.linesep)
            yaml_config_file.write("---")
            yaml_config_file.write(os.linesep)
            yaml_config_file.write(yaml_config)
            yaml_config_file.flush()

            rendered = run(["ytt"] + input_files_args + config.data["ytt.args"],
                           check=True,
                           stdout=PIPE, stderr=PIPE)

            with open(target_path, "wb") as output_file:
                output_file.write(rendered.stdout)
        finally:
            yaml_config_file.close()
