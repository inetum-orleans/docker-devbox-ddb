import os

import pytest

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.utils import file
from ddb.utils.file import FileWalker, FileUtils


class TestHasSameContent:
    def test_should_return_true_if_same_content(self, data_dir: str):
        file.has_same_content(os.path.join(data_dir, "512bytes.bin"), os.path.join(data_dir, "512bytes.copy.bin"))

    def test_should_return_false_if_different_content(self, data_dir: str):
        file.has_same_content(os.path.join(data_dir, "512bytes.bin"), os.path.join(data_dir, "1KB.bin"))

    def test_should_raise_file_not_found_error_if_file_doesnt_exists(self, data_dir: str):
        with pytest.raises(FileNotFoundError):
            file.has_same_content(os.path.join(data_dir, "512bytes.bin"), os.path.join(data_dir, "another.bin"))


class TestFileWalker:
    def test_should_exclude_files_in_excluded_directory(self):
        fw = FileWalker([], ["**/node_modules"], [], ".")
        assert fw.is_source_filtered("blabla/node_modules") is True
        assert fw.is_source_filtered("blabla/node_modules/file") is True
        assert fw.is_source_filtered("blabla/node_modules/subdirectory/file") is True
        assert fw.is_source_filtered("blabla/another/subdirectory/file") is False


class TestFileUtils:
    def test_get_file_content(self, data_dir: str, project_loader):
        project_loader()
        features.register(CoreFeature())
        load_registered_features()

        url = 'https://raw.githubusercontent.com/gfi-centre-ouest/docker-devbox-ddb/develop/tox.ini'
        path = 'test_file_content.txt'

        expected_file_content = '\n'.join([
            '# content of: tox.ini , put in same dir as setup.py',
            '[tox]',
            'envlist = py35,py36,py37,py38',
            'requires = tox-venv',
            '           setuptools >= 30.0.0',
            '',
            '[testenv]',
            'deps = -r requirements-dev.txt',
            'commands =',
            '  pylint ddb',
            '  pytest',
        ])

        url_content = FileUtils.get_file_content(url)
        assert expected_file_content == url_content

        url_content = FileUtils.get_file_content('file://' + os.path.join(config.path.project_home, path))
        assert url_content == 'this is a file for test_file_content'

        url_content = FileUtils.get_file_content('file://' + path)
        assert url_content == 'this is a file for test_file_content'
