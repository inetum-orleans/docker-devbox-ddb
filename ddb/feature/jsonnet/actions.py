# -*- coding: utf-8 -*-
import json
import os
from typing import Tuple, Union, Iterable

import yaml
from _jsonnet import evaluate_file  # pylint: disable=no-name-in-module

from ddb.action.action import AbstractTemplateAction
from ddb.config import config
from ddb.config.flatten import flatten
from ddb.feature import features
from ddb.utils.file import TemplateFinder


class JsonnetAction(AbstractTemplateAction):
    """
    Render jsonnet files based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "jsonnet:render"

    def _build_template_finder(self) -> TemplateFinder:
        return TemplateFinder(config.data.get("jsonnet.includes"),
                              config.data.get("jsonnet.excludes"),
                              config.data.get("jsonnet.suffixes"))

    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        """
        Render jsonnet template
        """
        # TODO: Add support for jsonnet CLI if _jsonnet native module is not available.
        evaluated = self._evaluate_jsonnet(template)

        multiple_file_output, multiple_file_dir = JsonnetAction._parse_multiple_header(template, target)
        if multiple_file_output:
            for (filename, content) in json.loads(evaluated).items():
                evaluated_target_path = os.path.join(multiple_file_dir, filename)
                evaluated_target_parent_path = os.path.dirname(evaluated_target_path)
                if evaluated_target_parent_path and not os.path.exists(evaluated_target_parent_path):
                    os.makedirs(evaluated_target_parent_path)

                yield content, evaluated_target_path
        else:
            ext = os.path.splitext(target)[-1]
            if ext.lower() in ['.yaml', '.yml']:
                evaluated = yaml.dump(json.loads(evaluated), Dumper=yaml.SafeDumper)
            yield evaluated, target

    @staticmethod
    def _evaluate_jsonnet(template_path):
        flatten_config = flatten(config.data, stop_for_features=features.all())
        ext_vars = {k: v for (k, v) in flatten_config.items() if isinstance(v, str)}
        ext_codes = {k: str(v).lower() if isinstance(v, bool) else str(v) if v is not None else "null"
                     for (k, v) in flatten_config.items() if not isinstance(v, str)}
        evaluated = evaluate_file(template_path,
                                  ext_vars=ext_vars,
                                  ext_codes=ext_codes,
                                  jpathdir=os.path.join(os.path.dirname(__file__), "lib"))
        return evaluated

    @staticmethod
    def _parse_multiple_header(template_path, target_path):
        multiple_file_output = False
        multiple_file_dir = None
        with open(template_path, 'r', encoding="utf-8") as template:
            first_line = template.readline()
            if first_line.startswith('// multiple-file-output'):
                multiple_file_output = True
                multiple_file_dir = os.path.dirname(target_path)
            first_line_splitted = first_line.rsplit(":", 1)
            if len(first_line_splitted) > 1:
                multiple_file_dir = first_line_splitted[-1].strip()
        return multiple_file_output, multiple_file_dir
