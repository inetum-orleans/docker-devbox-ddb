# -*- coding: utf-8 -*-
import os

import pytest
from _pytest.capture import CaptureFixture

from ddb.script import exec_script, exec_scripts


def test_exec_script_pass(data_dir: str):
    exec_script(os.path.join(data_dir, "pass.py"))


def test_exec_script_print(data_dir: str, capsys: CaptureFixture):
    exec_script(os.path.join(data_dir, "print.py"))
    captured = capsys.readouterr()
    assert captured.out == "print\n"
    assert captured.err == ""


def test_exec_script_compile_error(data_dir: str):
    with pytest.raises(NameError):
        exec_script(os.path.join(data_dir, "compile_error.py"))


def test_exec_script_context(data_dir: str, capsys: CaptureFixture):
    exec_script(os.path.join(data_dir, "context.py"), __locals={'test': 'testing'})
    captured = capsys.readouterr()
    assert captured.out == "testing\n"
    assert captured.err == ""


def test_exec_import_ddb(data_dir: str, capsys: CaptureFixture):
    exec_script(os.path.join(data_dir, "import_ddb.py"))
    captured = capsys.readouterr()
    assert captured.out == "ddb\n"
    assert captured.err == ""


def test_exec_scripts(data_dir: str, capsys: CaptureFixture):
    files = [
        os.path.join(data_dir, "folder1", "01-test1.py"),
        os.path.join(data_dir, "folder2", "05-test2.py"),
        os.path.join(data_dir, "folder2", "08-test3.py"),
        os.path.join(data_dir, "folder1", "10-test4.py"),
        os.path.join(data_dir, "folder2", "15-test5.py")
    ]
    exec_scripts(files)
    captured = capsys.readouterr()
    assert captured.out == "\n".join([
        "folder1.test1",
        "folder2.test2",
        "folder2.test3",
        "folder1.test4",
        "folder2.test5",
        ""
    ])
    assert captured.err == ""
