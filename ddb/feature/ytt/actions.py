# -*- coding: utf-8 -*-
import os
import tempfile
from typing import Union, Iterable, Tuple

import yaml

from ddb.action.action import AbstractTemplateAction
from ddb.config import config
from ddb.utils.file import TemplateFinder
from ddb.utils.process import run


class YttAction(AbstractTemplateAction):
    """
    Render ytt files based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "ytt:render"

    def _build_template_finder(self):
        return TemplateFinder(config.data.get("ytt.includes"),
                              config.data.get("ytt.excludes"),
                              config.data.get("ytt.suffixes"))

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

    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        yaml_config = yaml.dump(YttAction._escape_config(config.data.to_dict()))

        includes = TemplateFinder.build_default_includes_from_suffixes(
            config.data["ytt.depends_suffixes"],
            config.data["ytt.extensions"]
        )
        template_finder = TemplateFinder(includes, [], config.data["ytt.depends_suffixes"],
                                         os.path.dirname(target),
                                         recursive=False, skip_processed_targets=False)

        depends_files = [template[0] for template in template_finder.items]
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

            rendered = run("ytt", *input_files_args, *config.data["ytt.args"])

            yield rendered, target
        finally:
            os.unlink(yaml_config_file.name)
