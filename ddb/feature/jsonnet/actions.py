# -*- coding: utf-8 -*-
import json
import os
from typing import Union, Iterable, Callable

import yaml
from _jsonnet import evaluate_file  # pylint: disable=no-name-in-module
from marshmallow import Schema
from marshmallow.fields import Nested, Dict, List

from ddb.action import InitializableAction
from ddb.config import config
from ddb.event import bus
from ddb.feature import features
from ddb.utils.file import TemplateFinder


class JsonnetAction(InitializableAction):
    """
    Render jsonnet files based on filename suffixes.
    """

    def __init__(self):
        super().__init__()
        self.template_finder = None  # type: TemplateFinder

    @property
    def name(self) -> str:
        return "jsonnet:render"

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return ("file:found", self.on_file_found), \
               ("file:generated", self.on_file_generated), \
               ("jsonnet:render", self.render_jsonnet)

    def initialize(self):
        self.template_finder = TemplateFinder(config.data.get("jsonnet.includes"),
                                              config.data.get("jsonnet.excludes"),
                                              config.data.get("jsonnet.suffixes"))

    def on_file_found(self, file: str):
        """
        Called when a file is found.
        """
        template = file
        target = self.template_finder.get_target(template)
        if target:
            bus.emit('jsonnet:render', template=template, target=target)

    def on_file_generated(self, source: str, target: str):  # pylint:disable=unused-argument
        """
        Called when a file is generated.
        """
        template = target
        target = self.template_finder.get_target(template)
        if target:
            bus.emit('jsonnet:render', template=template, target=target)

    @staticmethod
    def _get_stop_fields_from_schema(schema: Schema, stack, ret):
        for field_name, field in schema.fields.items():
            stack.append(field_name)
            if isinstance(field, Dict):
                ret.append(tuple(stack))
            if isinstance(field, List):
                ret.append(tuple(stack))
            if isinstance(field, Nested):
                JsonnetAction._get_stop_fields_from_schema(field.schema, stack, ret)
            stack.pop()

    @staticmethod
    def _get_stop_fields():
        ret = []
        stack = []
        for feature in features.all():
            stack.append(feature.name)
            JsonnetAction._get_stop_fields_from_schema(feature.schema(), stack, ret)
            stack.pop()

        return ret

    def render_jsonnet(self, template: str, target: str):
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
                if not os.path.exists(evaluated_target_parent_path):
                    os.makedirs(evaluated_target_parent_path)
                with open(evaluated_target_path, 'w') as evaluated_target:
                    evaluated_target.write(content)
                self.template_finder.mark_as_processed(template, evaluated_target_path)
                bus.emit('file:generated', source=template, target=evaluated_target_path)
        else:
            ext = os.path.splitext(target)[-1]
            if ext.lower() in ['.yaml', '.yml']:
                evaluated = yaml.dump(json.loads(evaluated), Dumper=yaml.SafeDumper)
            with open(target, 'w') as target_file:
                target_file.write(evaluated)
            self.template_finder.mark_as_processed(template, target)
            bus.emit('file:generated', source=template, target=target)

    @staticmethod
    def _evaluate_jsonnet(template_path):
        flatten_config = config.flatten(stop_for=tuple(map(".".join, JsonnetAction._get_stop_fields())))
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
        with open(template_path, 'r') as template:
            first_line = template.readline()
            if first_line.startswith('// multiple-file-output'):
                multiple_file_output = True
                multiple_file_dir = os.path.dirname(target_path)
            first_line_splitted = first_line.rsplit(":", 1)
            if len(first_line_splitted) > 1:
                multiple_file_dir = first_line_splitted[-1].strip()
        return multiple_file_output, multiple_file_dir
