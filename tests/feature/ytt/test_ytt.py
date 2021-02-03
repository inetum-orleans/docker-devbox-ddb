import os

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.config import migrations, config
from ddb.config.migrations import PropertyMigration
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.file import FileFeature, FileWalkAction
from ddb.feature.ytt import YttFeature


class TestYttAction:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

    def test_plain(self, project_loader):
        project_loader("plain")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('yaml.yml')
        with open('yaml.yml', 'r') as f:
            rendered = f.read()

        with open('yaml.expected.yml', 'r') as f:
            expected = f.read()

        assert rendered == expected

    def test_config_variables(self, project_loader):
        project_loader("config_variables")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('variables.yaml')
        with open('variables.yaml', 'r') as f:
            rendered = f.read()

        with open('variables.expected.yaml', 'r') as f:
            expected = f.read()

        assert rendered == expected

    def test_ignore_invalid_extension(self, project_loader):
        project_loader("ignore_invalid_extension")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert not os.path.exists('yaml.txt')
        assert not os.path.exists('yaml.yml')

    def test_depends_suffixes(self, project_loader):
        project_loader("depends_suffixes")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('variables.yaml')
        with open('variables.yaml', 'r') as f:
            rendered = f.read()

        with open('variables.expected.yaml', 'r') as f:
            expected = f.read()

        assert rendered == expected


class TestYttAutofix:
    def teardown_method(self, test_method):
        migrations.set_history()

    def test_autofix_variables_only(self, project_loader):
        project_loader("autofix_variables_only")

        config.args.autofix = True

        history = (
            PropertyMigration("old_property",
                              "new_property", since="v1.1.0"),
            PropertyMigration("some.deep.old.property",
                              "some.another.new.property", since="v1.1.0"),
        )

        migrations.set_history(history)

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(YttFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('variables.yaml')
        with open('variables.yaml', 'r') as f:
            rendered = f.read()

        with open('variables.expected.yaml', 'r') as f:
            expected = f.read()

        assert expected == rendered

        with open('variables.ytt.yaml', 'r') as f:
            source = f.read()

        with open('variables.yaml.autofix', 'r') as f:
            fixed = f.read()

        assert source == fixed
