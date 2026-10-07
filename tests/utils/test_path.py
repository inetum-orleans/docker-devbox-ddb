import os
from pathlib import Path

from ddb.utils.path import absolute_path


class TestAbsolutePath:
    def test_relative_path_is_resolved_against_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        assert absolute_path("some/file.txt") == str(tmp_path / "some" / "file.txt")

    def test_absolute_path_is_kept(self, tmp_path):
        assert absolute_path(tmp_path / "file.txt") == str(tmp_path / "file.txt")

    def test_navigation_parts_are_normalized(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        assert absolute_path("./some/../file.txt") == str(tmp_path / "file.txt")

    def test_symlinks_are_not_expanded(self, tmp_path):
        target = tmp_path / "target"
        target.mkdir()
        link = tmp_path / "link"
        link.symlink_to(target)

        assert absolute_path(link / "file.txt") == str(link / "file.txt")

    def test_matches_os_path_abspath(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        # PTH100: the point of this test is that absolute_path matches os.path.abspath.
        for candidate in ("file.txt", "./file.txt", "a/../b", "/absolute/file.txt", "", "."):
            assert absolute_path(candidate) == os.path.abspath(candidate)  # noqa: PTH100

    def test_accepts_path_objects(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        assert absolute_path(Path("file.txt")) == str(tmp_path / "file.txt")
