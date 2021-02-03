# -*- coding: utf-8 -*-
import json
import os
import re
from typing import Tuple, Union, Iterable, Optional

import yaml
from _jsonnet import evaluate_file  # pylint: disable=no-name-in-module

from ddb.action.action import AbstractTemplateAction
from ddb.config import config, migrations
from ddb.config.flatten import flatten
from ddb.feature import features
from ddb.utils.file import TemplateFinder, SingleTemporaryFile


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

    def _autofix_render_error(self,
                              template: str,
                              target: str,
                              original_template: str,
                              render_error: Exception) -> Optional[str]:
        property_name_match = re.match('RUNTIME ERROR: undefined external variable: (.*)\n', str(render_error))
        if property_name_match:
            property_name = property_name_match.group(1)

            property_migration = migrations.get_migration_from_old_config_key(property_name)

            if property_migration and not property_migration.requires_value_migration:
                property_migration.warn(original_template)

                with open(template, "r", encoding="utf-8") as template_file:
                    initial_template_data = template_file.read()
                    template_data = initial_template_data
                    template_data = template_data.replace('std.extVar("' + property_migration.old_config_key + '")',
                                                          'std.extVar("' + property_migration.new_config_key + '")')
                    template_data = template_data.replace("std.extVar('" + property_migration.old_config_key + "')",
                                                          "std.extVar('" + property_migration.new_config_key + "')")

                if initial_template_data != template_data:
                    with SingleTemporaryFile("ddb", "migration", "jsonnet",
                                             mode="w",
                                             prefix="",
                                             suffix="." + os.path.basename(original_template),
                                             encoding="utf-8") as tmp_file:
                        tmp_file.write(template_data)
                        return tmp_file.name

        return None

    @staticmethod
    def _evaluate_jsonnet(template_path):
        data = config.data.copy()

        vars_config = flatten(data, stop_for_features=features.all())
        codes_config = flatten(data, keep_primitive_list=True, stop_for_features=features.all())
        codes_config['_config.eject'] = config.eject
        codes_config['_config.args'] = vars(config.args)
        codes_config['_config.unknown_args'] = config.unknown_args
        ext_vars = {k: v for (k, v) in vars_config.items() if isinstance(v, str)}
        ext_codes = {k: str(v).lower() if isinstance(v, bool) else str(v) if v is not None else "null"
                     for (k, v) in codes_config.items() if not isinstance(v, str)}
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
