from pathlib import Path

from ddb.__main__ import main
from tests.utilstest import expect_gitignore


class TestCopy:
    def test_copy(self, project_loader):
        project_loader("copy")

        main(["configure"])

        main(["activate"])

        assert Path("destination/test1").exists()
        assert Path("destination/test2").exists()

        assert expect_gitignore(".gitignore", "/destination/test1", "/destination/test2")

        Path("destination/test1").unlink()

        main(["configure"])

        assert Path("destination/test1").exists()
        assert Path("destination/test2").exists()
        assert expect_gitignore(".gitignore", "/destination/test1", "/destination/test2")
