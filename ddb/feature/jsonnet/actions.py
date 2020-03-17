# -*- coding: utf-8 -*-
import json
import os

import yaml
from _jsonnet import evaluate_file  # pylint: disable=no-name-in-module

from ddb.action import Action
from ddb.config import config
from ddb.event import bus
from ddb.utils.file import TemplateFinder


class RenderAction(Action):
    """
    Render jsonnet files based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "jsonnet:render"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    def execute(self, *args, **kwargs):
        generator = TemplateFinder(config.data["jsonnet.includes"],
                                   config.data["jsonnet.excludes"],
                                   config.data["jsonnet.suffixes"])

        for template, target in generator.templates:
            self._render_jsonnet(template, target)

    @staticmethod
    def _render_jsonnet(template_path: str, target_path: str):
        flatten_config = config.flatten()
        evaluated = evaluate_file(template_path, ext_vars=flatten_config)

        multiple_file_output, multiple_file_dir = RenderAction._parse_multiple_header(template_path, target_path)
        if multiple_file_output:
            for (filename, content) in json.loads(evaluated).items():
                evaluated_target_path = os.path.join(multiple_file_dir, filename)
                evaluated_target_parent_path = os.path.dirname(evaluated_target_path)
                if not os.path.exists(evaluated_target_parent_path):
                    os.makedirs(evaluated_target_parent_path)
                with open(evaluated_target_path, 'w') as evaluated_target:
                    evaluated_target.write(content)
                bus.emit('event:file-generated', source=template_path, target=evaluated_target)
        else:
            ext = os.path.splitext(target_path)[-1]
            if ext.lower() in ['.yaml', '.yml']:
                evaluated = yaml.dump(json.loads(evaluated), Dumper=yaml.SafeDumper)
            with open(target_path, 'w') as target:
                target.write(evaluated)
            bus.emit('event:file-generated', source=template_path, target=target)

    @staticmethod
    def _parse_multiple_header(template_path, target_path):
        multiple_file_output = False
        multiple_file_dir = None
        with open(template_path, 'r') as template:
            first_line = template.readline()
            if first_line.startswith('// multiple-file-output'):
                multiple_file_output = True
                multiple_file_dir = os.path.dirname(target_path)
            first_line_splitted = first_line.rsplit(":", 1)
            if len(first_line_splitted) > 1:
                multiple_file_dir = first_line_splitted[-1].strip()
        return multiple_file_output, multiple_file_dir
