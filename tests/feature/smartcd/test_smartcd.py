from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from ddb.__main__ import load_registered_features, main
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.shell import ShellFeature
from ddb.feature.smartcd import SmartcdAction, SmartcdFeature, WindowsProjectActivate


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


@pytest.mark.skipif("os.name != 'nt'")
class TestWindowsProjectActivate:
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

    def test_empty_project_main(self, project_loader):
        project_loader("empty")

        main(["configure"])

        assert Path("ddb_activate.bat").exists()
        assert Path("ddb_deactivate.bat").exists()

        with Path("ddb_activate.bat").open() as f:
            assert "set command=(ddb activate)" in f.read()

        with Path("ddb_deactivate.bat").open() as f:
            assert "set command=(ddb deactivate)" in f.read()
