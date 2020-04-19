# -*- coding: utf-8 -*-
import json
import os

import yaml
from _jsonnet import evaluate_file  # pylint: disable=no-name-in-module

from ddb.action import InitializableAction
from ddb.action.action import EventBinding
from ddb.config import config
from ddb.config.flatten import flatten
from ddb.event import bus
from ddb.feature import features
from ddb.utils.file import TemplateFinder, write_if_different


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
    def event_bindings(self):
        def file_found_processor(file: str):
            """
            Called when a file is found.
            """
            template = file
            target = self.template_finder.get_target(template)
            if target:
                return (), {"template": template, "target": target}
            return None

        def file_generated_processor(source: str, target: str):
            """
            Called when a file is generated.
            """
            template = target
            target = self.template_finder.get_target(template)
            if target:
                return (), {"template": template, "target": target}
            return None

        return (EventBinding("file:found", self.render_jsonnet, file_found_processor),
                EventBinding("file:generated", self.render_jsonnet, file_generated_processor))

    def initialize(self):
        self.template_finder = TemplateFinder(config.data.get("jsonnet.includes"),
                                              config.data.get("jsonnet.excludes"),
                                              config.data.get("jsonnet.suffixes"))

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
                if evaluated_target_parent_path and not os.path.exists(evaluated_target_parent_path):
                    os.makedirs(evaluated_target_parent_path)

                written = write_if_different(evaluated_target_path, content, log_source=template)
                self.template_finder.mark_as_processed(template, evaluated_target_path)
                if written:
                    bus.emit('file:generated', source=template, target=evaluated_target_path)
        else:
            ext = os.path.splitext(target)[-1]
            if ext.lower() in ['.yaml', '.yml']:
                evaluated = yaml.dump(json.loads(evaluated), Dumper=yaml.SafeDumper)

            written = write_if_different(target, evaluated, log_source=template)
            self.template_finder.mark_as_processed(template, target)

            if written:
                bus.emit('file:generated', source=template, target=target)

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
        with open(template_path, 'r') as template:
            first_line = template.readline()
            if first_line.startswith('// multiple-file-output'):
                multiple_file_output = True
                multiple_file_dir = os.path.dirname(target_path)
            first_line_splitted = first_line.rsplit(":", 1)
            if len(first_line_splitted) > 1:
                multiple_file_dir = first_line_splitted[-1].strip()
        return multiple_file_output, multiple_file_dir
