import os
import stat

import pytest

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.file import FileFeature, FileWalkAction
from ddb.feature.permissions import PermissionsFeature


@pytest.mark.skipif("os.name == 'nt'")
class TestPermissionsAction:
    def test_project(self, project_loader):
        project_loader("project")
        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(PermissionsFeature())

        load_registered_features()
        register_actions_in_event_bus()

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert stat.S_IMODE(os.lstat("script.sh").st_mode) == int('775', 8)
        assert stat.S_IMODE(os.lstat(os.path.join("subdirectory", "another-script.sh")).st_mode) == int('664', 8)

    def test_project2(self, project_loader):
        project_loader("project2")
        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(PermissionsFeature())

        load_registered_features()
        register_actions_in_event_bus()

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert stat.S_IMODE(os.lstat("script.sh").st_mode) == int('775', 8)
        assert stat.S_IMODE(os.lstat(os.path.join("subdirectory", "another-script.sh")).st_mode) == int('775', 8)

    def test_project3(self, project_loader):
        project_loader("project3")
        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(PermissionsFeature())

        load_registered_features()
        register_actions_in_event_bus()

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert stat.S_IMODE(os.lstat("script.sh").st_mode) == int('775', 8)
        assert stat.S_IMODE(os.lstat(os.path.join("subdirectory", "another-script.sh")).st_mode) == int('775', 8)
