import os

from ddb.__main__ import main


class TestPlugin:
    def test_copy_ca_certificates(self, project_loader):
        project_loader("feature")

        assert not os.path.exists("test")
        assert not os.path.exists("test2")
        assert not os.path.exists("test3")
        assert not os.path.exists("some")

        main(["configure"])

        assert os.path.exists("test")
        assert os.path.exists("test2")
        assert os.path.exists("test3")
        assert os.path.exists("some")
