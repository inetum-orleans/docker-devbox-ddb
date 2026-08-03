from pathlib import Path

import pytest

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.utils import file
from ddb.utils.file import FileUtils, FileWalker


class TestHasSameContent:
    def test_should_return_true_if_same_content(self, data_dir: str):
        file.has_same_content(str(Path(data_dir) / "512bytes.bin"), str(Path(data_dir) / "512bytes.copy.bin"))

    def test_should_return_false_if_different_content(self, data_dir: str):
        file.has_same_content(str(Path(data_dir) / "512bytes.bin"), str(Path(data_dir) / "1KB.bin"))

    def test_should_raise_file_not_found_error_if_file_doesnt_exists(self, data_dir: str):
        with pytest.raises(FileNotFoundError):
            file.has_same_content(str(Path(data_dir) / "512bytes.bin"), str(Path(data_dir) / "another.bin"))


class TestFileWalker:
    def test_should_exclude_files_in_excluded_directory(self):
        fw = FileWalker([], ["**/node_modules"], [], [], [], ".")
        assert fw.is_source_filtered("blabla/node_modules") is True
        assert fw.is_source_filtered("blabla/node_modules/file") is True
        assert fw.is_source_filtered("blabla/node_modules/subdirectory/file") is True
        assert fw.is_source_filtered("blabla/another/subdirectory/file") is False

    def test_includes_are_compiled_as_glob_patterns(self):
        fw = FileWalker(["*.txt", "*.md"], [], [], [], [], ".")
        assert fw._is_included("readme.txt", *fw.includes) is True
        assert fw._is_included("readme.md", *fw.includes) is True
        assert fw._is_included("readme.rst", *fw.includes) is False


class TestFileUtils:
    def test_get_file_content(self, data_dir: str, project_loader):
        project_loader()
        features.register(CoreFeature())
        load_registered_features()

        url = "https://raw.githubusercontent.com/inetum-orleans/docker-devbox-ddb/b4f11276a37a4e4b1142f6b54b3d0763ccf5639e/ddb/__init__.py"
        path = "test_file_content.txt"

        expected_file_content = "\n".join(["# -*- coding: utf-8 -*-", "", "from .__version__ import __version__", ""])

        url_content = FileUtils.get_file_content(url)
        assert expected_file_content == url_content

        url_content = FileUtils.get_file_content("file://" + str(Path(config.path.project_home) / path))
        assert url_content == "this is a file for test_file_content"

        url_content = FileUtils.get_file_content("file://" + path)
        assert url_content == "this is a file for test_file_content"
