import os
import shlex
import stat
from abc import ABC, abstractmethod
from typing import Tuple

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
    def set_environment_variable(self, key, value):
        """
        print an instruction that set an environment variable to shell.
        """

    @abstractmethod
    def remove_environment_variable(self, key):
        """
        print an instruction that unset an environment variable to shell.
        """

    @abstractmethod
    def remove_binary_shims(self, shims_path: str):
        """
        Remove all executable files matching binary shims.
        """

    @abstractmethod
    def create_binary_shim(self, shims_path: str, binary: Binary) -> Tuple[bool, str]:
        """
        Add a binary shim for this shell.
        :return created filepath
        """

    def header(self):
        """
        Header of script
        """

    def footer(self):
        """
        Footer of script
        """


class BashShellIntegration(ShellIntegration):
    """
    Bash integration.
    """

    def __init__(self):
        super().__init__("bash", "Bash")

    def set_environment_variable(self, key, value):
        print("export " + key + "=" + shlex.quote(value))

    def remove_environment_variable(self, key):
        print("unset " + key)

    def remove_binary_shims(self, shims_path: str):
        shims = []

        for shim in os.listdir(shims_path):
            with open(shim, "a", newline="\n") as shim_file:
                lines = shim_file.readlines()
                if len(lines) > 2 and lines[1] == "# ddb:shim":
                    shims.append(shim)

        for shim in shims:
            force_remove(shim)

    def create_binary_shim(self, shims_path: str, binary: Binary):
        os.makedirs(shims_path, exist_ok=True)
        shim = os.path.join(os.path.normpath(shims_path), binary.name)
        data = ''.join(["#!/usr/bin/env bash\n", "# ddb:shim\n", "$(ddb run %s) $@\n" % binary.name])
        written = write_if_different(shim, data)

        shim_stat = os.stat(shim)
        os.chmod(shim, shim_stat.st_mode | stat.S_IXUSR)
        return written, shim


class CmdShellIntegration(ShellIntegration):
    """
    Windows cmd integration
    """

    def __init__(self):
        super().__init__("cmd", "Windows cmd.exe")

    def set_environment_variable(self, key, value):
        print("set " + key + "=" + shlex.quote(value))  # TODO: Maybe use subprocess.list2cmdline for Windows ?

    def remove_environment_variable(self, key):
        print("set " + key + "=")

    def remove_binary_shims(self, shims_path: str):
        # TODO
        pass

    def create_binary_shim(self, shims_path: str, binary: Binary):
        # TODO
        pass
