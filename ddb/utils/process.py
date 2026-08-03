import os
import shlex
import subprocess

from ddb.config import config


def run(executable: str, *args: str):
    """
    Run executable using core.process configuration, replacing bin with configured one, appending and prepending args.
    """
    command_list = effective_command(executable, *args)
    process = subprocess.run(command_list,
                             check=True,
                             capture_output=True)
    if os.name == "nt":
        # On windows, there's ANSI code after output that has to be dropped...
        try:
            eof_index = process.stdout.index(b"\x1b[0m")
            process.stdout = process.stdout[:eof_index]
        except ValueError:
            pass
    return process.stdout


def effective_command(executable: str, *args: str) -> list[str]:
    """
    Get subprocess.run arguments using core.process configuration, replacing bin with configured one, appending and
    prepending args.
    """
    if not args:
        executable, *args = shlex.split(executable)

    configured_executable = config.data.get(f"core.process.{executable}.bin", executable)
    prepend_args = config.data.get(f"core.process.{executable}.prepend", [])
    append_args = config.data.get(f"core.process.{executable}.append", [])

    if os.name == 'nt' and not configured_executable.endswith('.exe'):
        configured_executable = f"{configured_executable}.exe"

    if isinstance(prepend_args, str):
        prepend_args = shlex.split(prepend_args)

    if isinstance(append_args, str):
        append_args = shlex.split(append_args)

    return [configured_executable, *prepend_args, *list(args), *append_args]
