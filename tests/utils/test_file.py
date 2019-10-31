import os

import pytest

from ddb.utils import file


class TestHasSameContent:
    def test_should_return_true_if_same_content(self, data_dir: str):
        file.has_same_content(os.path.join(data_dir, "512bytes.bin"), os.path.join(data_dir, "512bytes.copy.bin"))

    def test_should_return_false_if_different_content(self, data_dir: str):
        file.has_same_content(os.path.join(data_dir, "512bytes.bin"), os.path.join(data_dir, "1KB.bin"))

    def test_should_raise_file_not_found_error_if_file_doesnt_exists(self, data_dir: str):
        with pytest.raises(FileNotFoundError):
            file.has_same_content(os.path.join(data_dir, "512bytes.bin"), os.path.join(data_dir, "another.bin"))
