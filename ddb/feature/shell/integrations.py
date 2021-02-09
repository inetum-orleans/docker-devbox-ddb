import os
import shlex
import subprocess
from abc import ABC, abstractmethod
from typing import Tuple, Iterable, Dict, Any, Optional

from slugify import slugify

from ddb.binary import Binary
from ddb.config import config
from ddb.utils.file import force_remove, write_if_different, chmod


class ShellIntegration(ABC):
    """
    Interface for shell integration.
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def set_environment_variable(self, key, value) -> Iterable[str]:
        """
        Returns an instruction that set an environment variable to shell.
        """

    @abstractmethod
    def remove_environment_variable(self, key) -> Iterable[str]:
        """
        Returns an instruction that unset an environment variable to shell.
        """

    @abstractmethod
    def remove_binary_shim(self, shims_path: str, name: str) -> Optional[str]:
        """
        Delete a binary shim for this shell.
        @return removed filepath
        """

    @abstractmethod
    def create_binary_shim(self, shims_path: str, name: str, global_: bool) -> Tuple[bool, str]:
        """
        Add a binary shim for this shell.
        :return created filepath
        """

    @abstractmethod
    def create_alias_binary_shim(self, shims_path: str, binary: Binary) -> Tuple[bool, str]:
        """
        Add a alias binary shim for this shell.
        :return created filepath
        """

    @abstractmethod
    def evaluate_script(self, script_filepath) -> Iterable[str]:
        """
        Get the command to evaluate the script inside the current shell context.
        """

    @abstractmethod
    def generate_and_operator(self, new_line: bool = False) -> str:
        """
        Build the shell command to run the given command inside the current shell context.
        """

    @abstractmethod
    def generate_or_operator(self, new_line: bool = False) -> str:
        """
        Build the shell command to run the given command inside the current shell context.
        """

    @abstractmethod
    def generate_cmdline(self, command: Iterable[str], system_path=True) -> str:
        """
        Build the shell command to run the given command inside the current shell context.
        """

    def before_environ_backup(self, environ: Dict[str, str]):
        """
        Alter environment variables before backup. This should be used to remove for saved environ variables that
        should not be restored on deactivation.
        """

    def header(self) -> Iterable[str]:  # pylint:disable=no-self-use
        """
        Returns header of script
        """
        yield from ()

    def footer(self) -> Iterable[str]:  # pylint:disable=no-self-use
        """
        Returns footer of script
        """
        yield from ()

    @property
    def temporary_file_kwargs(self) -> Dict[str, Any]:
        """
        Additional options for temporary file
        """
        return {}


class BashShellIntegration(ShellIntegration):
    """
    Bash integration.
    """

    def __init__(self):
        super().__init__("bash", "Bash")

    @staticmethod
    def _sanitize_key(key):
        return slugify(key, regex_pattern=r'[^-a-zA-Z0-9_]+', separator="_").upper()

    def set_environment_variable(self, key, value):
        yield "export " + self._sanitize_key(key) + "=" + shlex.quote(value)

    def remove_environment_variable(self, key):
        yield "unset " + self._sanitize_key(key)

    def remove_binary_shim(self, shims_path: str, name: str) -> Optional[str]:
        shim = os.path.join(shims_path, name)
        if not os.path.isfile(shim):
            return None
        force_remove(shim)
        return shim

    def create_binary_shim(self, shims_path: str, name: str, global_: bool):
        if global_:
            ddb_project_home_variable = next(
                self.set_environment_variable(config.env_prefix + "_PROJECT_HOME", config.paths.project_home)
            )

            compose_ignore_orphans_variable = next(
                self.set_environment_variable("COMPOSE_IGNORE_ORPHANS", "1")
            )

            command = f"$(ddb deactivate --force)\n" \
                      f"{ddb_project_home_variable}\n" \
                      f"{compose_ignore_orphans_variable}\n" \
                      f"$(ddb activate --force)\n" \
                      f"$(ddb run {name} \"$@\")"
        else:
            command = f"$(ddb run {name} \"$@\")"

        return self._write_shim(shims_path, name, 'binary', command)

    def create_alias_binary_shim(self, shims_path: str, binary: Binary) -> Tuple[bool, str]:
        return self._write_shim(shims_path, binary.name, 'alias', binary.command())

    @staticmethod
    def _write_shim(shims_path: str, shim_name: str, shim_type: str, command: Iterable[str]) -> Tuple[bool, str]:
        """
        Generate the shim file
        :return:
        """
        os.makedirs(shims_path, exist_ok=True)
        shim = os.path.join(os.path.normpath(shims_path), shim_name)

        content = '\n'.join(["#!/usr/bin/env bash", "# ddb:shim:" + shim_type, ''.join(command) + " \"$@\""]) + "\n"

        written = write_if_different(shim, content, newline="\n")

        chmod(shim, '+x', logging=False)
        return written, shim

    @property
    def temporary_file_kwargs(self) -> Dict[str, Any]:
        return {"encoding": "utf-8", "newline": '\n'}

    def evaluate_script(self, script_filepath) -> Iterable[str]:
        yield ". %s" % (script_filepath,)

    def generate_and_operator(self, new_line: bool = False) -> str:
        return " &&" + ("\\" if new_line else " ")

    def generate_or_operator(self, new_line: bool = False) -> str:
        return " ||" + ("\\" if new_line else " ")

    def generate_cmdline(self, command: Iterable[str], system_path=True) -> str:
        return subprocess.list2cmdline(command)


class CmdShellIntegration(ShellIntegration):
    """
    Windows cmd integration
    """

    def __init__(self):
        super().__init__("cmd", "Windows cmd.exe")

    @staticmethod
    def _sanitize_key(key):
        return slugify(key, regex_pattern=r'[^-a-zA-Z0-9_]+', separator="_").upper()

    def set_environment_variable(self, key, value):
        # TODO: Maybe use subprocess.list2cmdline for Windows ?
        yield "set " + self._sanitize_key(key) + "=" + value.replace('\n', '!NL! ^\n')

    def remove_environment_variable(self, key):
        yield "set " + self._sanitize_key(key) + "="

    def remove_binary_shim(self, shims_path: str, name: str) -> Optional[str]:
        shim = os.path.join(shims_path, name + '.bat')
        if not os.path.isfile(shim):
            return None
        force_remove(shim)
        return shim

    def create_binary_shim(self, shims_path: str, name: str, global_: bool):
        commands = []
        if global_:
            commands.extend([
                "set command=(ddb deactivate --force)",
                "%command%>cmd.txt",
                "set /p execution=<cmd.txt",
                "del cmd.txt",
                "%execution%"
            ])

            commands.append(next(
                self.set_environment_variable(config.env_prefix + "_PROJECT_HOME", config.paths.project_home)
            ))

            commands.append(next(
                self.set_environment_variable("COMPOSE_IGNORE_ORPHANS", "1")
            ))

            commands.extend([
                "set command=(ddb activate --force)",
                "%command%>cmd.txt",
                "set /p execution=<cmd.txt",
                "del cmd.txt",
                "%execution%"
            ])

        commands.extend([
            f"set command=(ddb run {name} \"%*\")",
            "%command%>cmd.txt",
            "set /p execution=<cmd.txt",
            "del cmd.txt",
            "%execution% \"%*\""
        ])

        return self._write_shim(shims_path, name, 'binary', commands)

    def create_alias_binary_shim(self, shims_path: str, binary: Binary):
        return self._write_shim(shims_path, binary.name, 'alias', binary.command())

    @staticmethod
    def _write_shim(shims_path: str, shim_name: str, shim_type: str, command: Iterable[str]) -> Tuple[bool, str]:
        """
        Generate the shim file
        :return:
        """
        os.makedirs(shims_path, exist_ok=True)
        shim = os.path.join(os.path.normpath(shims_path), shim_name + '.bat')

        content = '\n'.join(["@echo off", "REM ddb:shim:" + shim_type, "SHIFT", '\n'.join(command)]) + "\n"

        written = write_if_different(shim, content, newline="\n")

        chmod(shim, '+x', logging=False)
        return written, shim

    def evaluate_script(self, script_filepath) -> Iterable[str]:
        yield "call %s" % (script_filepath,)

    def header(self) -> Iterable[str]:
        return ["@echo off", "set NL=^", ""]

    def generate_and_operator(self, new_line: bool = False) -> str:
        return " &&" + ("\\" if new_line else " ")

    def generate_or_operator(self, new_line: bool = False) -> str:
        return " ||" + ("\\" if new_line else " ")

    def generate_cmdline(self, command: Iterable[str], system_path=True) -> str:
        return subprocess.list2cmdline(command)
