import os
import stat

import pytest

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.jinja import JinjaFeature
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

        assert os.access("script.sh", os.X_OK)
        assert not os.access(os.path.join("subdirectory", "another-script.sh"), os.X_OK)

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

        assert os.access("script.sh", os.X_OK)
        assert os.access(os.path.join("subdirectory", "another-script.sh"), os.X_OK)

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

        assert os.access("script.sh", os.X_OK)
        assert os.access(os.path.join("subdirectory", "another-script.sh"), os.X_OK)
        assert os.access(os.path.join("subdirectory"), os.W_OK)
        assert not os.access(os.path.join("denied"), os.W_OK)

    def test_inherit_from_template(self, project_loader):
        project_loader("inherit_from_template")
        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        features.register(PermissionsFeature())

        load_registered_features()
        register_actions_in_event_bus()

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists("script.sh")
        assert os.access("script.sh", os.X_OK)
