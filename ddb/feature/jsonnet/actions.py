# -*- coding: utf-8 -*-
import json
import os

import yaml
from _jsonnet import evaluate_file  # pylint: disable=no-name-in-module
from marshmallow import Schema
from marshmallow.fields import Nested, Dict, List

from ddb.action import Action
from ddb.config import config
from ddb.event import bus
from ddb.feature import features
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
    def _get_stop_fields_from_schema(schema: Schema, stack, ret):
        for field_name, field in schema.fields.items():
            stack.append(field_name)
            if isinstance(field, Dict):
                ret.append(tuple(stack))
            if isinstance(field, List):
                ret.append(tuple(stack))
            if isinstance(field, Nested):
                RenderAction._get_stop_fields_from_schema(field.schema, stack, ret)
            stack.pop()

    @staticmethod
    def _get_stop_fields():
        ret = []
        stack = []
        for feature in features.all():
            stack.append(feature.name)
            RenderAction._get_stop_fields_from_schema(feature.schema(), stack, ret)
            stack.pop()

        return ret

    @staticmethod
    def _render_jsonnet(template_path: str, target_path: str):
        # TODO: Add support for jsonnet CLI if _jsonnet native module is not available.

        flatten_config = config.flatten(stop_for=tuple(map(".".join, RenderAction._get_stop_fields())))
        ext_vars = {k: v for (k, v) in flatten_config.items() if isinstance(v, str)}
        ext_codes = {k: str(v).lower() if isinstance(v, bool) else str(v)
                     for (k, v) in flatten_config.items() if not isinstance(v, str)}

        evaluated = evaluate_file(template_path,
                                  ext_vars=ext_vars,
                                  ext_codes=ext_codes,
                                  jpathdir=os.path.join(os.path.dirname(__file__), "lib"))

        multiple_file_output, multiple_file_dir = RenderAction._parse_multiple_header(template_path, target_path)
        if multiple_file_output:
            for (filename, content) in json.loads(evaluated).items():
                evaluated_target_path = os.path.join(multiple_file_dir, filename)
                evaluated_target_parent_path = os.path.dirname(evaluated_target_path)
                if not os.path.exists(evaluated_target_parent_path):
                    os.makedirs(evaluated_target_parent_path)
                with open(evaluated_target_path, 'w') as evaluated_target:
                    evaluated_target.write(content)
                bus.emit('event:file-generated', source=template_path, target=evaluated_target_path)
        else:
            ext = os.path.splitext(target_path)[-1]
            if ext.lower() in ['.yaml', '.yml']:
                evaluated = yaml.dump(json.loads(evaluated), Dumper=yaml.SafeDumper)
            with open(target_path, 'w') as target:
                target.write(evaluated)
            bus.emit('event:file-generated', source=template_path, target=target_path)

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
