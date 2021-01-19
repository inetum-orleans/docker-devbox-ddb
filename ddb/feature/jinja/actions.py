# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path
from typing import Union, Iterable, Tuple, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ddb.config import config, migrations
from ddb.utils.file import TemplateFinder, SingleTemporaryFile, get_single_temporary_file_directory
from . import filters, tests
from ...action.action import AbstractTemplateAction
from ...config.migrations import AbstractPropertyMigration

custom_filters = vars(filters)
for k in tuple(custom_filters.keys()):
    if k.startswith("__"):
        del custom_filters[k]

custom_tests = vars(tests)
for k in tuple(custom_tests.keys()):
    if k.startswith("__"):
        del custom_tests[k]


class JinjaAction(AbstractTemplateAction):
    """
    Render jinja templates based on filename suffixes.
    """

    def __init__(self):
        super().__init__()
        self.env = None  # type: Environment
        self.context = None  # type: dict
        self._rootpath = None  # type: str
        self._migrationpath = None  # type: str

    @property
    def name(self) -> str:
        return "jinja:render"

    def _build_template_finder(self):
        return TemplateFinder(config.data.get("jinja.includes"),
                              config.data.get("jinja.excludes"),
                              config.data.get("jinja.suffixes"))

    def initialize(self):
        super().initialize()

        self._rootpath = self.template_finder.rootpath
        self._migrationpath = get_single_temporary_file_directory("ddb", "migration", "jinja")

        effective_options = {
            "loader": FileSystemLoader([self._rootpath, self._migrationpath]),
            "undefined": StrictUndefined,
            "keep_trailing_newline": True
        }

        options = config.data.get('jinja.options')
        if options:
            effective_options.update(options)

        self.env = Environment(**effective_options)

        self.env.filters.update(custom_filters)
        self.env.tests.update(custom_tests)

        self.context = config.data.copy()
        self.context['_config'] = dict()
        self.context['_config.eject'] = config.eject
        self.context['_config.args'] = vars(config.args)
        self.context['_config.unknown_args'] = config.unknown_args

    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        if template.startswith(self._migrationpath):
            template_name = os.path.relpath(os.path.normpath(template),
                                            os.path.normpath(str(self._migrationpath)))

        else:
            template_name = os.path.relpath(os.path.normpath(template),
                                            os.path.normpath(str(self._rootpath)))

        template_name = Path(template_name).as_posix()
        jinja = self.env.get_template(template_name)
        yield jinja.render(**self.context), target

    def _autofix_render_error(self,
                              template: str,
                              target: str,
                              original_template: str,
                              render_error: Exception) -> Optional[str]:
        property_migration_set = set()
        undefined_match = re.match("'(.*)' is undefined", str(render_error))
        if undefined_match:
            property_name = undefined_match.group(1)
            property_migration = migrations.get_migration_from_old_config_key(property_name)
            if property_migration:
                property_migration_set.add(property_migration)
        else:
            dict_object_match = re.match("'dict object' has no attribute '(.*)'", str(render_error))
            if dict_object_match:
                property_contains = f".{dict_object_match.group(1)}"

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

                    template_data = template_data.replace(property_migration.old_config_key,
                                                          property_migration.new_config_key)

            if initial_template_data != template_data:
                with SingleTemporaryFile("ddb", "migration", "jinja",
                                         mode="w",
                                         prefix="",
                                         suffix=".jinja",
                                         encoding="utf-8") as tmp_file:
                    tmp_file.write(template_data)
                    return tmp_file.name

        return None
