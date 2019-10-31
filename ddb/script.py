# -*- coding: utf-8 -*-
from typing import Iterable


def exec_script(file: str, __globals: dict = None, __locals: dict = None):  # pylint:disabled:redefined-builtin
    """
    Execute a python script from source file.
    :param file: filepath to python script
    :param __globals: globals
    :param __locals: locals
    """
    if __globals is None:
        __globals = {}
    if __locals is None:
        __locals = {}

    with open(file, "rb") as source_fp:
        code = compile(source_fp.read(), file, 'exec')
        exec(code, __globals, __locals)  # pylint:disable=exec-used


def exec_scripts(files: Iterable[str], __globals: dict = None, __locals: dict = None):
    """
    Execute many python scripts from source file.
    :param files: filepath to python scripts
    :param __globals: globals
    :param __locals:  locals
    """
    for file in files:
        exec_script(file, __globals, __locals)
