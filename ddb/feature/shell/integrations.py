import os
import shlex
import stat
from abc import ABC, abstractmethod
from typing import Tuple, Iterable, Dict, Any

from ddb.binary import Binary
from ddb.utils.file import force_remove, write_if_different


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
    def remove_all_binary_shims(self, shims_path: str):
        """
        Remove all executable files matching binary shims.
        """

    @abstractmethod
    def remove_binary_shim(self, shims_path: str, binary: Binary) -> bool:
        """
        Delete a binary shim for this shell.
        """

    @abstractmethod
    def create_binary_shim(self, shims_path: str, binary: Binary) -> Tuple[bool, str]:
        """
        Add a binary shim for this shell.
        :return created filepath
        """

    @abstractmethod
    def evaluate_script(self, script_filepath) -> Iterable[str]:
        """
        Get the command to evaluate the script inside the current shell context.
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

    def set_environment_variable(self, key, value):
        yield "export " + key + "=" + shlex.quote(value)

    def remove_environment_variable(self, key):
        yield "unset " + key

    def remove_all_binary_shims(self, shims_path: str):
        shims = []

        for shim in os.listdir(shims_path):
            with open(shim, "a", encoding="utf-8", newline="\n") as shim_file:
                lines = shim_file.readlines()
                if len(lines) > 2 and lines[1] == "# ddb:shim":
                    shims.append(shim)

        for shim in shims:
            force_remove(shim)

    def remove_binary_shim(self, shims_path: str, binary: Binary) -> bool:
        shim = os.path.join(shims_path, binary.name)
        if not os.path.isfile(shim):
            return False
        force_remove(os.path.join(shims_path, binary.name))
        return True

    def create_binary_shim(self, shims_path: str, binary: Binary):
        os.makedirs(shims_path, exist_ok=True)
        shim = os.path.join(os.path.normpath(shims_path), binary.name)
        data = ''.join(["#!/usr/bin/env bash\n", "# ddb:shim\n", "$(ddb run %s \"$@\") \"$@\"\n" % binary.name])
        written = write_if_different(shim, data, newline="\n")

        shim_stat = os.stat(shim)
        os.chmod(shim, shim_stat.st_mode | stat.S_IXUSR)
        return written, shim

    @property
    def temporary_file_kwargs(self) -> Dict[str, Any]:
        return {"encoding": "utf-8", "newline": '\n'}

    def evaluate_script(self, script_filepath) -> Iterable[str]:
        yield "source %s" % (script_filepath,)


class CmdShellIntegration(ShellIntegration):
    """
    Windows cmd integration
    """

    def __init__(self):
        super().__init__("cmd", "Windows cmd.exe")

    def set_environment_variable(self, key, value):
        yield "set " + key + "=" + shlex.quote(value)  # TODO: Maybe use subprocess.list2cmdline for Windows ?

    def remove_environment_variable(self, key):
        yield "set " + key + "="

    def remove_all_binary_shims(self, shims_path: str):
        # TODO
        pass

    def remove_binary_shim(self, shims_path: str, binary: Binary) -> bool:
        # TODO
        pass

    def create_binary_shim(self, shims_path: str, binary: Binary):
        # TODO
        pass

    def evaluate_script(self, script_filepath) -> Iterable[str]:
        yield "source %s" % (script_filepath,)
