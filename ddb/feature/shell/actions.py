# -*- coding: utf-8 -*-
import json
import os

from dictdiffer import diff

from .integrations import ShellIntegration
from ...action import Action
from ...config import config

_env_environ_backup = config.env_prefix + "_SHELL_ENVIRON_BACKUP"


def apply_diff_to_shell(shell: ShellIntegration, source_environment: dict, target_environment: dict):
    """
    Compute and apply environment diff for given shell.
    """
    for (action, source, dest_items) in diff(source_environment, target_environment):
        if action == 'add':
            for (key, value) in dest_items:
                shell.set_environment_variable(key, value)
        if action == 'change':
            shell.set_environment_variable(source, dest_items[1])
        if action == 'remove':
            for (key, value) in dest_items:
                shell.remove_environment_variable(key)


class ActivateAction(Action):
    """
    Generates activation script
    """

    def __init__(self, shell: ShellIntegration):
        self.shell = shell

    @property
    def event_name(self) -> str:
        return "phase:print-activate"

    @property
    def name(self) -> str:
        return self.shell.name + "-print-activate"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def run(self, *args, **kwargs):
        environ_backup = dict(os.environ)
        os.environ[_env_environ_backup] = json.dumps(environ_backup)

        config_environ = config.to_environ()
        os.environ.update(config_environ)

        apply_diff_to_shell(self.shell, environ_backup, os.environ)


class DeactivateAction(Action):
    """
    Generations deactivation script
    """

    def __init__(self, shell: ShellIntegration):
        self.shell = shell

    @property
    def event_name(self) -> str:
        return "phase:print-deactivate"

    @property
    def name(self) -> str:
        return self.shell.name + "-print-deactivate"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def run(self, *args, **kwargs):
        environ_backup = json.loads(os.environ[_env_environ_backup])
        apply_diff_to_shell(self.shell, os.environ, environ_backup)
