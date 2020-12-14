# -*- coding: utf-8 -*-
import os
import shutil
import zipfile
from pathlib import Path
from typing import Callable, Optional

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempPathFactory
from ddb.__main__ import reset, configure_logging
from ddb.config import Config
from pytest_mock import MockerFixture
from verboselogs import SPAM

from .utilstest import init_config_paths, load_config

pytest_plugins = ["docker_compose"]


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
def project_loader(data_dir: str, tmp_path_factory: TempPathFactory, request: FixtureRequest) -> Callable[
    [Optional[str]], Config]:
    def load(name: str = None, before_load_config=None, config_provider=init_config_paths):
        root_dir = os.path.join(data_dir, name) if name else data_dir

        tmp_path = tmp_path_factory.mktemp(request.function.__name__)  # type: Path
        tmp_path.rmdir()
        shutil.copytree(root_dir, str(tmp_path))

        os.chdir(str(tmp_path))
        if before_load_config:
            before_load_config()
        conf = config_provider(str(tmp_path))
        os.chdir(str(conf.paths.project_home))

        if os.path.exists("repo.zip"):
            with zipfile.ZipFile("repo.zip", 'r') as zip_ref:
                zip_ref.extractall(".")

        return conf

    return load


@pytest.fixture(autouse=True)
def configure(mocker: MockerFixture):
    original_environ = dict(os.environ)
    cwd = os.getcwd()

    Config.defaults = {'defaults': {'fail_fast': True}}

    try:
        if os.name == 'nt' and 'COMSPEC' not in os.environ:
            os.environ['COMSPEC'] = r'C:\Windows\System32\cmd.exe'
        if os.name != 'nt' and 'SHELL' not in os.environ:
            os.environ['SHELL'] = '/bin/bash'
        if os.name == 'nt':
            os.environ['DDB_OVERRIDE_DOCKER_USER_UID'] = '1000'
            os.environ['DDB_OVERRIDE_DOCKER_USER_GID'] = '1000'
            os.environ['DDB_OVERRIDE_DOCKER_IP'] = '127.0.0.1'

        configure_logging(SPAM)

        mocker.patch('ddb.feature.smartcd.actions.is_smartcd_installed', lambda: False)
        mocker.patch('ddb.feature.version.is_git_repository', lambda: False)

        yield
    finally:
        os.chdir(cwd)
        os.environ.clear()
        os.environ.update(original_environ)
        reset()
