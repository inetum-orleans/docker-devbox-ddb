# -*- coding: utf-8 -*-
import base64
import json
import os
from typing import Iterable

import zgitignore
from dictdiffer import diff

from .integrations import ShellIntegration
from ...action import Action, actions
from ...action.action import EventBinding
from ...binary import Binary, binaries
from ...binary.binary import DefaultBinary
from ...config import config
from ...config.flatten import to_environ
from ...context import context
from ...event import events
from ...utils.file import SingleTemporaryFile

_env_environ_backup = config.env_prefix + "_SHELL_ENVIRON_BACKUP"


def get_shims_path(global_: bool = False):
    """
    Get local or global shims path.
    :param global_:
    :return:
    """
    directories = config.data.get('shell.path.directories')

    if global_:
        shim_directory_prefix = config.paths.home
        forbidden_shim_directory_prefix = config.paths.project_home
    else:
        shim_directory_prefix = config.paths.project_home
        forbidden_shim_directory_prefix = None

    shim_directory = None
    for directory in directories:
        if not os.path.isabs(directory):
            directory = os.path.join(config.paths.project_home, directory)
        if directory.startswith(shim_directory_prefix) and \
                (not forbidden_shim_directory_prefix or
                 not directory.startswith(forbidden_shim_directory_prefix)):
            shim_directory = directory
            break

    return shim_directory


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


def remove_from_system_path(shell: ShellIntegration, paths: Iterable[str]) -> Iterable[str]:
    """
    Remove given path to system PATH environment variable
    """
    system_path = os.environ.get('PATH', '')
    for path in paths:
        if config.data.get('shell.path.prepend'):
            system_path = system_path.replace(path + os.pathsep, "")
        else:
            system_path = system_path.replace(os.pathsep + path, "")

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
        if not binaries.has(binary.name):
            # Remove shim only if no binary are remaining for this name
            removed = self.shell.remove_binary_shim(directories[0], binary.name)
            if removed:
                events.file.deleted(removed)

    def execute(self, binary: Binary):
        """
        Create binary shim
        """
        shims_path = get_shims_path(binary.global_)
        written, shim = self.shell.create_binary_shim(shims_path, binary.name, binary.global_)
        if written:
            context.log.success("Shim created: %s", shim)
        else:
            context.log.notice("Shim exists: %s", shim)

        if written or config.eject:
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
        aliases = config.data.get('shell.aliases')
        global_aliases = frozenset(config.data.get('shell.global_aliases'))
        for alias in aliases:
            global_alias = alias in global_aliases

            shim_directory = get_shims_path(global_alias)
            if not shim_directory:
                continue

            binary = DefaultBinary(alias, aliases[alias])
            written, shim = self.shell.create_alias_binary_shim(shim_directory, binary)
            if written:
                context.log.success("Shim created: %s", shim)
            else:
                context.log.notice("Shim exists: %s", shim)

            if not global_alias:
                if written or config.eject:
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

    def _deactivate(self):
        deactivate_action = actions.get("shell:" + self.shell.name + ":deactivate")
        deactivate_action.execute()

    def execute(self):
        """
        Execute action
        """
        try:
            check_activated('force' not in config.args or not config.args.force)
            if config.args.force:
                self._deactivate()
            else:
                raise CheckIsActivatedException("project is already activated.")
        except CheckIsNotActivatedException:
            pass

        initial_environ = dict(os.environ.items())
        config_environ = to_environ(config.data, config.env_prefix)
        config_environ.update(config.env_additions)

        to_encode_environ = dict(initial_environ)
        self.shell.before_environ_backup(to_encode_environ)
        os.environ.update(config_environ)
        os.environ[_env_environ_backup] = encode_environ_backup(to_encode_environ)
        os.environ[config.env_prefix + '_PROJECT_HOME'] = config.paths.project_home

        with SingleTemporaryFile("ddb", "activate",
                                 mode='w',
                                 prefix="",
                                 suffix="." + self.shell.name,
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
        try:
            check_activated('force' not in config.args or not config.args.force)
        except CheckAnotherProjectActivatedException:
            pass

        if os.environ.get(_env_environ_backup):
            environ_backup = decode_environ_backup(os.environ[_env_environ_backup])

            with SingleTemporaryFile("ddb", "deactivate",
                                     mode='w',
                                     prefix="",
                                     suffix="." + self.shell.name,
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


class CheckActivatedException(Exception):
    """
    Exception for activated check
    """


class CheckIsActivatedException(CheckActivatedException):
    """
    Exception for activated check
    """


class CheckIsNotActivatedException(CheckActivatedException):
    """
    Exception for activated check
    """


class CheckAnotherProjectActivatedException(CheckActivatedException):
    """
    Exception for activated check
    """


def check_activated(do_raise=False, do_log=False):
    """
    Check if project is activated in current shell.
    :return:
    """
    project_home_key = config.env_prefix + '_PROJECT_HOME'

    if project_home_key in os.environ:
        if os.environ[project_home_key] == config.paths.project_home:
            if do_log:
                context.log.info("Project is activated.")
            return True
        try:
            raise CheckAnotherProjectActivatedException(
                "Another project is already activated (%s)" % os.environ[project_home_key])
        except CheckAnotherProjectActivatedException as exc:
            if do_log:
                context.log.error(str(exc))
            if do_raise:
                raise exc
        return False

    try:
        raise CheckIsNotActivatedException("Project is not activated")
    except CheckIsNotActivatedException as exc:
        if do_log:
            context.log.error(str(exc))
        if do_raise:
            raise exc
        return False


class CheckActivatedAction(Action):
    """
    Check if project is activated in current shell
    """

    def __init__(self, shell: ShellIntegration):
        super().__init__()
        self.shell = shell

    @property
    def event_bindings(self):
        return "phase:check-activated"

    @property
    def name(self) -> str:
        return "shell:" + self.shell.name + ":check-activated"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def execute(self):  # pylint:disable=no-self-use
        """
        Execute action
        """
        try:
            check_activated(True, True)
        except CheckActivatedException as exc:
            context.exceptions.append(exc)


class CommandAction(Action):
    """
    Display a requested command for it to be evaluated by the shell
    """

    def __init__(self, shell: ShellIntegration):
        super().__init__()
        self.shell = shell

    @property
    def event_bindings(self):
        return events.run.command

    @property
    def name(self) -> str:
        return "shell:" + self.shell.name + ":command"

    @property
    def description(self) -> str:
        return super().description + " for " + self.shell.description

    @property
    def disabled(self) -> bool:
        return config.data.get('shell.shell') != self.shell.name

    def execute(self, command: Iterable[str], system_path: bool = False):
        """
        Execute action
        """
        if not system_path:
            print(self.shell.generate_cmdline(command))
            return

        path_additions = None

        with SingleTemporaryFile("ddb", "run",
                                 mode='w',
                                 prefix="",
                                 suffix="." + self.shell.name,
                                 **self.shell.temporary_file_kwargs) as file:
            script_filepath = file.name
            if system_path:
                path_directories = config.data.get('shell.path.directories')
                if path_directories:
                    path_additions = map(
                        lambda path_addition: os.path.normpath(os.path.join(config.paths.project_home, path_addition)),
                        path_directories)
                    for instruction in remove_from_system_path(self.shell, path_additions):
                        print(instruction, file=file)
                    print(file=file)

            print(self.shell.generate_cmdline(command), end="", file=file)

            if path_additions:
                or_generated = False
                for instruction in add_to_system_path(self.shell, path_additions):
                    if not or_generated:
                        print(self.shell.generate_or_operator(True), file=file)
                    else:
                        print(self.shell.generate_and_operator(True), file=file)
                    print(instruction, end="", file=file)

            print(file=file)

        for ins in self.shell.evaluate_script(script_filepath):
            print(ins)
