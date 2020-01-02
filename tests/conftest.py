# -*- coding: utf-8 -*-
import os
from typing import Callable, Union, Optional, Any

import pytest
import shutil
from _pytest.fixtures import FixtureRequest
from pathlib import Path

from _pytest.tmpdir import TempPathFactory

from ddb.__main__ import reset
from ddb.config import Config
from .utilstest import load_config


@pytest.fixture(scope="module")
def global_data_dir(request: FixtureRequest) -> str:
    filename = request.module.__file__
    dirname = os.path.dirname(filename)
    return os.path.join(os.path.join(dirname, "data"))


@pytest.fixture(scope="module")
def data_dir(global_data_dir: str, request: FixtureRequest) -> str:
    filename = request.module.__file__
    dirname = os.path.dirname(global_data_dir)
    data_dirname, _ = os.path.splitext(os.path.basename(filename))
    return os.path.join(dirname, data_dirname + ".data")


@pytest.fixture()
def config_loader(data_dir: str) -> Callable[[Optional[str]], Config]:
    def load(name: str = None):
        return load_config(data_dir, name)
    return load


@pytest.fixture()
def project_loader(data_dir: str, tmp_path_factory: TempPathFactory, request: FixtureRequest) -> Callable[[Optional[str]], Config]:
    def load(name: str = None):
        root_dir = os.path.join(data_dir, name) if name else data_dir

        tmp_path = tmp_path_factory.mktemp(request.function.__name__)  # type: Path
        tmp_path.rmdir()
        shutil.copytree(root_dir, str(tmp_path))

        os.chdir(str(tmp_path))
        return load_config(str(tmp_path))

    return load


@pytest.fixture(autouse=True)
def configure():
    original_environ = dict(os.environ)
    cwd = os.getcwd()

    try:
        if os.name == 'nt' and 'COMSPEC' not in os.environ:
            os.environ['COMSPEC'] = r'C:\Windows\System32\cmd.exe'
        if os.name != 'nt' and 'SHELL' not in os.environ:
            os.environ['SHELL'] = '/bin/bash'
        if os.name == 'nt':
            os.environ['DDB_OVERRIDE_DOCKER_USER_UID'] = '1000'
            os.environ['DDB_OVERRIDE_DOCKER_USER_GID'] = '1000'

        yield
    finally:
        os.chdir(cwd)
        os.environ.clear()
        os.environ.update(original_environ)
        reset()
