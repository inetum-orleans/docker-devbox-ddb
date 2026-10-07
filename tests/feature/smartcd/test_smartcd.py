from pathlib import Path
from subprocess import CalledProcessError

import pytest
from pytest_mock import MockerFixture

from ddb.__main__ import load_registered_features, main
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.shell import ShellFeature
from ddb.feature.smartcd import SmartcdAction, SmartcdFeature, WindowsProjectActivate
from ddb.feature.smartcd.actions import is_smartcd_installed


class TestIsSmartcdInstalled:
    def test_smartcd_help_succeeds(self, mocker: MockerFixture):
        run = mocker.patch("ddb.feature.smartcd.actions.run", return_value=b"")

        assert is_smartcd_installed()
        run.assert_called_once_with("bash", "-ic", "smartcd", "--help")

    def test_smartcd_help_fails(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.smartcd.actions.run", side_effect=CalledProcessError(127, "bash"))

        assert not is_smartcd_installed()


@pytest.mark.skipif("os.name == 'nt'")
class TestSmartcdAction:
    def test_empty_project_without_core(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.smartcd.actions.is_smartcd_installed", lambda: True)

        project_loader("empty")

        features.register(SmartcdFeature())
        load_registered_features()

        action = SmartcdAction()
        action.execute()

        assert not Path(".bash_enter").exists()
        assert not Path(".bash_leave").exists()

    def test_empty_project_with_core(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.smartcd.actions.is_smartcd_installed", lambda: True)

        project_loader("empty")

        features.register(CoreFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = SmartcdAction()
        action.execute()

        assert not Path(".bash_enter").exists()
        assert not Path(".bash_leave").exists()

    def test_empty_project_with_activate_deactivate_commands(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.smartcd.actions.is_smartcd_installed", lambda: True)

        project_loader("empty")

        features.register(CoreFeature())
        features.register(ShellFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = SmartcdAction()
        action.execute()

        assert Path(".bash_enter").exists()
        assert Path(".bash_leave").exists()

        with Path(".bash_enter").open() as f:
            content = f.read()
            assert "$(ddb activate)" in content

        with Path(".bash_leave").open() as f:
            assert "$(ddb deactivate)" in f.read()

    def test_empty_project_main(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.smartcd.actions.is_smartcd_installed", lambda: True)

        project_loader("empty")

        main(["configure"])

        assert Path(".bash_enter").exists()
        assert Path(".bash_leave").exists()

        with Path(".bash_enter").open() as f:
            content = f.read()
            assert "$(ddb activate)" in content

        with Path(".bash_leave").open() as f:
            assert "$(ddb deactivate)" in f.read()

    def test_empty_project_main_no_smartcd(self, project_loader, mocker: MockerFixture):
        mocker.patch("ddb.feature.smartcd.actions.is_smartcd_installed", lambda: False)

        project_loader("empty")

        main(["configure"])

        assert not Path(".bash_enter").exists()
        assert not Path(".bash_leave").exists()


class TestWindowsProjectActivate:
    """
    The action itself only writes files, so it is exercised on every platform even though it is only enabled on
    windows.
    """

    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(SmartcdFeature())
        load_registered_features()

        action = WindowsProjectActivate()
        action.execute()

        assert not Path("ddb_activate.bat").exists()
        assert not Path("ddb_deactivate.bat").exists()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = WindowsProjectActivate()
        action.execute()

        assert not Path("ddb_activate.bat").exists()
        assert not Path("ddb_deactivate.bat").exists()

    def test_empty_project_with_activate_deactivate_commands(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(ShellFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = WindowsProjectActivate()
        action.execute()

        assert Path("ddb_activate.bat").exists()
        assert Path("ddb_deactivate.bat").exists()

        with Path("ddb_activate.bat").open() as f:
            assert "set command=(ddb activate)" in f.read()

        with Path("ddb_deactivate.bat").open() as f:
            assert "set command=(ddb deactivate)" in f.read()

    @pytest.mark.skipif("os.name != 'nt'")
    def test_empty_project_main(self, project_loader):
        project_loader("empty")

        main(["configure"])

        assert Path("ddb_activate.bat").exists()
        assert Path("ddb_deactivate.bat").exists()

        with Path("ddb_activate.bat").open() as f:
            assert "set command=(ddb activate)" in f.read()

        with Path("ddb_deactivate.bat").open() as f:
            assert "set command=(ddb deactivate)" in f.read()
