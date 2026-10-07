from pathlib import Path

from ddb.__main__ import main


class TestPlugin:
    def test_copy_ca_certificates(self, project_loader):
        project_loader("feature")

        assert not Path("test").exists()
        assert not Path("test2").exists()
        assert not Path("test3").exists()
        assert not Path("some").exists()

        main(["configure"])

        assert Path("test").exists()
        assert Path("test2").exists()
        assert Path("test3").exists()
        assert Path("some").exists()
