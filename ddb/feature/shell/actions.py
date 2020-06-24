# -*- coding: utf-8 -*-
import base64
import json
import os
from tempfile import NamedTemporaryFile, gettempdir
from typing import Iterable

import zgitignore
from dictdiffer import diff

from .integrations import ShellIntegration
from ...action import Action
from ...action.action import EventBinding
from ...binary import Binary
from ...binary.binary import DefaultBinary
from ...config import config
from ...config.flatten import to_environ
from ...context import context
from ...event import events

_env_environ_backup = config.env_prefix + "_SHELL_ENVIRON_BACKUP"


def encode_environ_backup(environ_backup: dict) -> str:
    """
    Encode environ backup into a safe string.
    """
    return base64.b64encode(json.dumps(environ_backup).encode("utf-8")).decode("utf-8")


def decode_environ_backup(encoded_environ_backup: str) -> dict:
    """
    Decode environ backup from safe string.
    """
    return json.loads(base64.b64decode(encoded_environ_backup).decode("utf-8"))


def apply_diff_to_shell(shell: ShellIntegration,
                        source_environment: dict,
                        target_environment: dict,
                        envignore=None) -> Iterable[str]:
    """
    Compute and apply environment diff for given shell, returning a list of shell instruction to run.
    """
    variables = []

    for (action, source, dest_items) in diff(source_environment, target_environment):
        if action == 'add':
            for (key, value) in dest_items:
                variables.append((key, value))
        if action == 'change':
            variables.append((source, dest_items[1]))
        if action == 'remove':
            for (key, value) in dest_items:
                variables.append((key, None))

    envignore_helper = None
    if envignore:
        envignore_helper = zgitignore.ZgitIgnore(envignore)

    for key, value in sorted(variables, key=lambda variable: variable[0]):
        if not envignore_helper or not envignore_helper.is_ignored(key):
            if value is None:
                yield from shell.remove_environment_variable(key)
            else:
                yield from shell.set_environment_variable(key, value)


def add_to_system_path(shell: ShellIntegration, paths: Iterable[str]) -> Iterable[str]:
    """
    Add given path to system PATH environment variable
    """
    system_path = os.environ.get('PATH', '')
    for path in paths:
        if config.data.get('shell.path.prepend'):
            system_path = path + os.pathsep + system_path
        else:
            system_path = system_path + os.pathsep + path

    yield from shell.set_environment_variable('PATH', system_path)


class CreateBinaryShim(Action):
    """
    Create binary shim for each generated binary
    """

    def __init__(self, shell: ShellIntegration):
        super().__init__()
        self.shell = shell

    @property
    def event_bindings(self):
        return (events.binary.registered,
                events.binary.found,
                EventBinding(events.binary.unregistered, call=self.remove))

    @property
    def name(self) -> str:
        return "shell:" + self.shell.name + ":create-binary-shim"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def remove(self, binary: Binary):
        """
        Remove binary shim
        """
        directories = config.data.get('shell.path.directories')
        self.shell.remove_binary_shim(directories[0], binary)

    def execute(self, binary: Binary):
        """
        Create binary shim
        """
        directories = config.data.get('shell.path.directories')
        written, shim = self.shell.create_binary_shim(directories[0], binary)
        if written:
            context.log.success("Shim created: %s", shim)
        else:
            context.log.notice("Shim exists: %s", shim)

        if written:
            events.file.generated(source=None, target=shim)


class CreateAliasShim(Action):
    """
    Create alias shim for each alias
    """

    def __init__(self, shell: ShellIntegration):
        super().__init__()
        self.shell = shell

    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def name(self) -> str:
        return "shell:" + self.shell.name + ":create-alias-shim"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def execute(self):
        """
        Create binary shim
        """
        directories = config.data.get('shell.path.directories')
        aliases = config.data.get('shell.aliases')
        shim_directory = directories[0]
        for key in aliases:
            binary = DefaultBinary(key, aliases[key])
            written, shim = self.shell.create_alias_binary_shim(shim_directory, binary)
            if written:
                context.log.success("Shim created: %s", shim)
            else:
                context.log.notice("Shim exists: %s", shim)

            if written:
                events.file.generated(source=None, target=shim)


class ActivateAction(Action):
    """
    Generates activation script
    """

    def __init__(self, shell: ShellIntegration):
        super().__init__()
        self.shell = shell

    @property
    def event_bindings(self):
        return "phase:activate"

    @property
    def name(self) -> str:
        return "shell:" + self.shell.name + ":activate"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    @property
    def order(self) -> int:
        return -256

    def execute(self):
        """
        Execute action
        """
        initial_environ = dict(os.environ.items())
        config_environ = to_environ(config.data, config.env_prefix)
        config_environ.update(config.env_additions)

        to_encode_environ = dict(initial_environ)
        os.environ.update(config_environ)
        os.environ[_env_environ_backup] = encode_environ_backup(to_encode_environ)
        os.environ[config.env_prefix + '_PROJECT_HOME'] = config.paths.project_home

        tempdir = os.path.join(gettempdir(), "ddb", "activate")
        os.makedirs(tempdir, exist_ok=True)

        with NamedTemporaryFile(mode='w',
                                dir=tempdir,
                                prefix="",
                                suffix="." + self.shell.name,
                                delete=False,
                                **self.shell.temporary_file_kwargs) as file:
            script_filepath = file.name
            file.writelines('\n'.join(self.shell.header()))
            file.write('\n')

            file.writelines('\n'.join(apply_diff_to_shell(
                self.shell,
                initial_environ,
                os.environ,
                config.data.get('shell.envignore'))))
            file.write('\n')

            path_directories = config.data.get('shell.path.directories')
            if path_directories:
                path_additions = map(
                    lambda path_addition: os.path.normpath(os.path.join(config.paths.project_home, path_addition)),
                    path_directories)
                file.writelines('\n'.join(add_to_system_path(self.shell, path_additions)))
                file.write('\n')

            file.writelines('\n'.join(self.shell.footer()))
            file.write('\n')

        for ins in self.shell.evaluate_script(script_filepath):
            print(ins)

        for previous_temporary_file in os.listdir(tempdir):
            previous_temporary_filepath = os.path.join(tempdir, previous_temporary_file)
            if previous_temporary_filepath != script_filepath:
                os.remove(previous_temporary_filepath)


class DeactivateAction(Action):
    """
    Generations deactivation script
    """

    def __init__(self, shell: ShellIntegration):
        super().__init__()
        self.shell = shell

    @property
    def event_bindings(self):
        return "phase:deactivate"

    @property
    def name(self) -> str:
        return "shell:" + self.shell.name + ":deactivate"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def execute(self):
        """
        Execute action
        """
        if os.environ.get(_env_environ_backup):
            environ_backup = decode_environ_backup(os.environ[_env_environ_backup])

            tempdir = os.path.join(gettempdir(), "ddb", "deactivate")
            os.makedirs(tempdir, exist_ok=True)

            with NamedTemporaryFile(mode='w',
                                    dir=tempdir,
                                    prefix="",
                                    suffix="." + self.shell.name,
                                    delete=False,
                                    **self.shell.temporary_file_kwargs) as file:
                script_filepath = file.name
                file.writelines('\n'.join(self.shell.header()))
                file.write('\n')

                file.writelines('\n'.join(apply_diff_to_shell(
                    self.shell,
                    os.environ,
                    environ_backup,
                    config.data.get('shell.envignore'))))
                file.write('\n')

                file.writelines('\n'.join(self.shell.footer()))
                file.write('\n')

            for ins in self.shell.evaluate_script(script_filepath):
                print(ins)

            for previous_temporary_file in os.listdir(tempdir):
                previous_temporary_filepath = os.path.join(tempdir, previous_temporary_file)
                if previous_temporary_filepath != script_filepath:
                    os.remove(previous_temporary_filepath)
