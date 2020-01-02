# -*- coding: utf-8 -*-
import fnmatch
import os
from pathlib import Path
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader

from ddb.action import Action
from ddb.config import config


class ConfigureAction(Action):
    """
    Creates symbolic links based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "jinja:configure"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    def run(self, *args, **kwargs):
        includes = config.data["jinja.includes"]
        excludes = config.data["jinja.excludes"]
        suffixes = config.data["jinja.suffixes"]

        rootpath = Path('.')

        env = Environment(
            loader=FileSystemLoader(str(rootpath))
        )

        context = dict(config.data)

        for include in includes:
            for template_candidate_path in rootpath.glob(include):
                template_candidate = str(template_candidate_path)

                if self._is_excluded(template_candidate, excludes):
                    continue

                target = self._get_target(template_candidate, suffixes)

                if target:
                    self._render_template(template_candidate, target, env, **context)

    @staticmethod
    def _is_excluded(template_candidate: str, excludes: List[str]) -> bool:
        excluded = False
        for exclude in excludes:
            if fnmatch.fnmatch(template_candidate, exclude):
                excluded = True
                break
        return excluded

    @staticmethod
    def _get_target(template_candidate: str, suffixes: List[str]) -> Optional[str]:
        basename, ext = os.path.splitext(template_candidate)
        if ext in suffixes:
            return basename

        if not ext and basename.startswith("."):
            ext = basename
            basename = ""

        for suffix in suffixes:
            if basename.endswith(suffix):
                return template_candidate[:len(basename) - len(suffix)] + ext

        return None

    @staticmethod
    def _render_template(template_path: str, target_path: str, env: Environment, **context):
        template = env.get_template(template_path)
        template.render(**context)

        with open(target_path, 'w') as target:
            target.write(template.render(**context))
