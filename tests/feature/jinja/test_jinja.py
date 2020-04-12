import os

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.file import FileFeature, FileWalkAction
from ddb.feature.jinja import JinjaFeature, JinjaAction


class TestJinjaAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_project1(self, project_loader):
        project_loader("project1")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('foo.yml')
        with open('foo.yml', 'r') as f:
            foo = f.read()

        assert foo == 'env: dev'

    def test_project2(self, project_loader):
        project_loader("project2")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('foo.yml')
        with open('foo.yml', 'r') as f:
            foo = f.read()

        assert foo == 'env: dev\nincluded: True'

        assert not os.path.exists(os.path.join("partial", "_partial.yml"))
        assert not os.path.exists(os.path.join("partial", "partial.yml"))

    def test_project3(self, project_loader):
        project_loader("project3")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('.foo.yml')
        with open('.foo.yml', 'r') as f:
            foo = f.read()

        assert foo == 'env: dev'

    def test_project4(self, project_loader):
        project_loader("project4")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('foo')
        with open('foo', 'r') as f:
            foo = f.read()

        assert foo == 'env=dev'

    def test_project5(self, project_loader):
        project_loader("project5")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('foo')
        with open('foo', 'r') as f:
            foo = f.read()
        assert foo == 'env=dev'

        assert os.path.exists('foo.yml')
        with open('foo.yml', 'r') as f:
            foo = f.read()

        assert foo == 'env: dev'
