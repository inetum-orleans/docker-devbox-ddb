import shlex

from abc import ABC, abstractmethod


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
