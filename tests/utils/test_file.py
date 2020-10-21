import os

import pytest
from ddb.utils import file
from ddb.utils.file import FileWalker


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
