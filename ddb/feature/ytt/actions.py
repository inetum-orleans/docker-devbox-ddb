# -*- coding: utf-8 -*-
import os
import re
import tempfile
from typing import Union, Iterable, Tuple, Optional

import yaml

from ddb.action.action import AbstractTemplateAction
from ddb.config import config, migrations
from ddb.config.migrations import AbstractPropertyMigration
from ddb.utils.file import TemplateFinder, SingleTemporaryFile
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
    def _escape_config(input_config: dict, with_config: bool = True):
        new = {}
        keywords = config.data["ytt.keywords"]
        keywords_escape_format = config.data["ytt.keywords_escape_format"]
        for key, value in input_config.items():
            if isinstance(value, dict):
                value = YttAction._escape_config(value, False)
            if key in keywords:
                escaped_k = keywords_escape_format % (key,)
                if escaped_k not in value.keys():
                    new[escaped_k] = value
            new[key] = value
        if with_config:
            new['_config'] = dict()
            new['_config']['eject'] = config.eject
            new['_config']['args'] = dict(vars(config.args))
            new['_config']['unknown_args'] = list(config.unknown_args)
        return new

    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        yaml_config = yaml.safe_dump(YttAction._escape_config(config.data.raw()))

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

    def _autofix_render_error(self,
                              template: str,
                              target: str,
                              original_template: str,
                              render_error: Exception) -> Optional[str]:
        if not hasattr(render_error, "stderr"):
            return None
        error_message = str(render_error.stderr, encoding="utf-8")

        property_migration_set = set()

        error_match = re.search(r"struct has no \.(.*?)\s+field or method", error_message)
        if error_match:
            property_contains = f"{error_match.group(1)}"

            for property_migration in migrations.get_history():
                if isinstance(property_migration, AbstractPropertyMigration) \
                        and not property_migration.requires_value_migration \
                        and property_contains in property_migration.old_config_key:
                    property_migration_set.add(property_migration)

        if property_migration_set:
            with open(template, "r", encoding="utf-8") as template_file:
                initial_template_data = template_file.read()
                template_data = initial_template_data

            for property_migration in property_migration_set:
                if property_migration and not property_migration.requires_value_migration:
                    property_migration.warn(original_template)

                    template_data = re.sub(r"(#@.*\s+)" +
                                           re.escape("data.values." + property_migration.old_config_key) +
                                           r"(.*?\s*.*?)",
                                           r"\1" + "data.values." + property_migration.new_config_key + r"\2",
                                           template_data)

            if initial_template_data != template_data:
                with SingleTemporaryFile("ddb", "migration", "ytt",
                                         mode="w",
                                         prefix="",
                                         suffix="." + os.path.basename(original_template),
                                         encoding="utf-8") as tmp_file:
                    tmp_file.write(template_data)
                    return tmp_file.name

        return None
