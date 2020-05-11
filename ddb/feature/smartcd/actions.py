import os
from subprocess import CalledProcessError
from typing import Union, Iterable, Callable

from ddb.action.action import EventBinding, InitializableAction
from ddb.command import commands
from ddb.event import events
from ddb.utils.file import write_if_different
from ddb.utils.process import run


def is_smartcd_installed():
    """
    Run smartcd command to check if it"s installed.
    """

    try:
        run("bash", "-ic", "smartcd", "--help")
        return True
    except CalledProcessError:
        return False


class SmartcdAction(InitializableAction):
    """
    Generate bash_enter/bash_leave files if smartcd is installed
    """

    @property
    def event_bindings(self) -> Union[Iterable[Union[Callable, str, EventBinding]], Union[Callable, str, EventBinding]]:
        return events.phase.configure

    @property
    def name(self) -> str:
        return "smartcd:generate"

    @property
    def disabled(self) -> bool:
        return os.name == 'nt'

    @staticmethod
    def execute():
        """
        Write .bash_enter/.bash_leave files.
        :return:
        """
        if not commands.has("activate") and not commands.has("deactivate"):
            return
        if not is_smartcd_installed():
            return

        if write_if_different(".bash_enter", "echo [smartcd] Activate\n$(ddb activate)\n"):
            events.file.generated(source=None, target=".bash_enter")

        if write_if_different(".bash_leave", "echo [smartcd] Deactivate\n$(ddb deactivate)\n"):
            events.file.generated(source=None, target=".bash_leave")


class WindowsProjectActivate(InitializableAction):
    """
    Generate ddb_activate.bat/ddb_deactivate.bat for windows environement
    TODO find and activate something equivalent to smartcd but for windows ?
    """

    @property
    def event_bindings(self) -> Union[Iterable[Union[Callable, str, EventBinding]], Union[Callable, str, EventBinding]]:
        return events.phase.configure

    @property
    def name(self) -> str:
        return "smartcd:windows:generate-project-activate"

    @property
    def disabled(self) -> bool:
        return os.name != 'nt'

    @staticmethod
    def execute():
        """
        Write .bash_enter/.bash_leave files.
        :return:
        """
        if not commands.has("activate") and not commands.has("deactivate"):
            return

        commands_activate = ["@echo off", "REM ddb:shim", "SHIFT", "set command=(ddb activate)", "%command%>cmd.txt",
                             "set /p execution=<cmd.txt", "del cmd.txt", "%execution% \"%*\""]
        command_activate = '\n'.join(commands_activate) + '\n'

        if write_if_different("ddb_activate.bat", command_activate):
            events.file.generated(source=None, target="ddb_activate.bat")

        commands_deactivate = ["@echo off", "REM ddb:shim", "SHIFT", "set command=(ddb deactivate)",
                               "%command%>cmd.txt", "set /p execution=<cmd.txt", "del cmd.txt", "%execution% \"%*\""]
        command_deactivate = '\n'.join(commands_deactivate) + '\n'

        if write_if_different("ddb_deactivate.bat", command_deactivate):
            events.file.generated(source=None, target="ddb_deactivate.bat")
