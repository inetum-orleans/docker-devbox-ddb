import os

from ddb.__main__ import main
from tests.utilstest import expect_gitignore


class TestCopy:
    def test_copy(self, project_loader):
        project_loader("copy")

        main(["configure"])

        main(["activate"])

        assert os.path.exists("destination/test1")
        assert os.path.exists("destination/test2")

        assert expect_gitignore('.gitignore', '/destination/test1', '/destination/test2')

        os.remove("destination/test1")

        main(["configure"])

        assert os.path.exists("destination/test1")
        assert os.path.exists("destination/test2")
        assert expect_gitignore('.gitignore', '/destination/test1', '/destination/test2')
