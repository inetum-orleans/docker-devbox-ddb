# -*- coding: utf-8 -*-
import os

from ddb.action import Action
from ddb.config import config


class ConfigureAction(Action):
    """
    Creates symbolic links based on filename suffixes.
    """

    @property
    def name(self) -> str:
        return "create-symlinks"

    @property
    def event_name(self) -> str:
        return "phase:configure"

    def execute(self, *args, **kwargs):
        targets = config.data["symlinks.targets"]
        current_suffix = config.data["symlinks.suffixes.current"]
        available_suffixes = config.data["symlinks.suffixes.available"]

        possible_suffixes = available_suffixes[available_suffixes.index(current_suffix):]

        for target in targets:
            basename, ext = os.path.splitext(target)
            if not ext and basename.startswith("."):
                ext = basename
                basename = ""

            for suffix in possible_suffixes:
                possible_filename = "{basename}.{suffix}{ext}".format(basename=basename, suffix=suffix, ext=ext)
                if os.path.exists(possible_filename):
                    os.symlink(possible_filename, target)
                    break
