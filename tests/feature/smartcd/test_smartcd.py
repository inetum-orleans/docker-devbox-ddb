import os

import pytest
from pytest_mock import MockFixture

from ddb.__main__ import main, load_registered_features
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.shell import ShellFeature
from ddb.feature.smartcd import SmartcdFeature, SmartcdAction, WindowsProjectActivate


@pytest.mark.skipif("os.name == 'nt'")
class TestSmartcdAction:
    def test_empty_project_without_core(self, project_loader, mocker: MockFixture):
        mocker.patch('ddb.feature.smartcd.actions.is_smartcd_installed', lambda: True)

        project_loader("empty")

        features.register(SmartcdFeature())
        load_registered_features()

        action = SmartcdAction()
        action.execute()

        assert not os.path.exists(".bash_enter")
        assert not os.path.exists(".bash_leave")

    def test_empty_project_with_core(self, project_loader, mocker: MockFixture):
        mocker.patch('ddb.feature.smartcd.actions.is_smartcd_installed', lambda: True)

        project_loader("empty")

        features.register(CoreFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = SmartcdAction()
        action.execute()

        assert not os.path.exists(".bash_enter")
        assert not os.path.exists(".bash_leave")

    def test_empty_project_with_activate_deactivate_commands(self, project_loader, mocker: MockFixture):
        mocker.patch('ddb.feature.smartcd.actions.is_smartcd_installed', lambda: True)

        project_loader("empty")

        features.register(CoreFeature())
        features.register(ShellFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = SmartcdAction()
        action.execute()

        assert os.path.exists(".bash_enter")
        assert os.path.exists(".bash_leave")

        with open(".bash_enter") as f:
            content = f.read()
            assert "$(ddb activate)" in content

        with open(".bash_leave") as f:
            assert "$(ddb deactivate)" in f.read()

    def test_empty_project_main(self, project_loader, mocker: MockFixture):
        mocker.patch('ddb.feature.smartcd.actions.is_smartcd_installed', lambda: True)

        project_loader("empty")

        main(["configure"])

        assert os.path.exists(".bash_enter")
        assert os.path.exists(".bash_leave")

        with open(".bash_enter") as f:
            content = f.read()
            assert "$(ddb activate)" in content

        with open(".bash_leave") as f:
            assert "$(ddb deactivate)" in f.read()

    def test_empty_project_main_no_smartcd(self, project_loader, mocker: MockFixture):
        mocker.patch('ddb.feature.smartcd.actions.is_smartcd_installed', lambda: False)

        project_loader("empty")

        main(["configure"])

        assert not os.path.exists(".bash_enter")
        assert not os.path.exists(".bash_leave")


@pytest.mark.skipif("os.name != 'nt'")
class TestWindowsProjectActivate:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(SmartcdFeature())
        load_registered_features()

        action = WindowsProjectActivate()
        action.execute()

        assert not os.path.exists("ddb_activate.bat")
        assert not os.path.exists("ddb_deactivate.bat")

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = WindowsProjectActivate()
        action.execute()

        assert not os.path.exists("ddb_activate.bat")
        assert not os.path.exists("ddb_deactivate.bat")

    def test_empty_project_with_activate_deactivate_commands(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(ShellFeature())
        features.register(SmartcdFeature())
        load_registered_features()

        action = WindowsProjectActivate()
        action.execute()

        assert os.path.exists("ddb_activate.bat")
        assert os.path.exists("ddb_deactivate.bat")

        with open("ddb_activate.bat") as f:
            assert "set command=(ddb activate)" in f.read()

        with open("ddb_deactivate.bat") as f:
            assert "set command=(ddb deactivate)" in f.read()

    def test_empty_project_main(self, project_loader):
        project_loader("empty")

        main(["configure"])

        assert os.path.exists("ddb_activate.bat")
        assert os.path.exists("ddb_deactivate.bat")

        with open("ddb_activate.bat") as f:
            assert "set command=(ddb activate)" in f.read()

        with open("ddb_deactivate.bat") as f:
            assert "set command=(ddb deactivate)" in f.read()
