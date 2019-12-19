# -*- coding: utf-8 -*-
import os

import pytest
from _pytest.fixtures import FixtureRequest

from ddb.__main__ import reset


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


@pytest.fixture(autouse=True)
def configure():
    original_environ = dict(os.environ)

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
        os.environ.clear()
        os.environ.update(original_environ)
        reset()
