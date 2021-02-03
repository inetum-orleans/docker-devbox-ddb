import os

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.config import config, migrations
from ddb.config.migrations import PropertyMigration
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.file import FileFeature, FileWalkAction
from ddb.feature.jinja import JinjaFeature


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

    def test_project_keep_trailing_lines_false(self, project_loader):
        project_loader("trailing-newline")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        config.data['jinja.options'] = {"keep_trailing_newline": False}

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('foo.yml')
        with open('foo.yml', 'r') as f:
            foo = f.read()

        assert foo == 'test: trailing'

    def test_project_keep_trailing_lines_default(self, project_loader):
        project_loader("trailing-newline")

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

        assert foo == 'test: trailing\n'

    def test_project_keep_trailing_lines_true(self, project_loader):
        project_loader("trailing-newline")

        features.register(CoreFeature())
        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        config.data['jinja.options'] = {"keep_trailing_newline": True}

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('foo.yml')
        with open('foo.yml', 'r') as f:
            foo = f.read()

        assert foo == 'test: trailing\n'


class TestJinjaAutofix:
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

        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        assert os.path.exists('config.properties')
        with open('config.properties', 'r') as f:
            rendered = f.read()

        with open('config.expected.properties', 'r') as f:
            expected = f.read()

        assert rendered == expected

        with open('config.properties.jinja', 'r') as f:
            source = f.read()

        with open('config.properties.autofix', 'r') as f:
            fixed = f.read()

        assert source == fixed

    def test_autofix_eol(self, project_loader):
        project_loader("autofix_eol")

        history = (
            PropertyMigration("docker.compose.network_name",
                              "jsonnet.docker.compose.network_name", since="v1.6.0"),
            PropertyMigration("docker.port_prefix",
                              "jsonnet.docker.expose.port_prefix", since="v1.6.0"),
        )

        migrations.set_history(history)

        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        with open('docker-compose.properties', 'r') as f:
            rendered = f.read()

        with open('docker-compose.expected.properties', 'r') as f:
            expected = f.read()

        assert rendered == expected

    def test_autofix_eol2(self, project_loader):
        project_loader("autofix_eol2")

        config.args.autofix = True

        history = (
            PropertyMigration("docker.compose.network_name",
                              "jsonnet.docker.compose.network_name", since="v1.6.0"),
            PropertyMigration("docker.port_prefix",
                              "jsonnet.docker.expose.port_prefix", since="v1.6.0"),
        )

        migrations.set_history(history)

        features.register(FileFeature())
        features.register(JinjaFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = FileWalkAction()
        action.initialize()
        action.execute()

        with open('msmtprc', 'r') as f:
            rendered = f.read()

        with open('msmtprc.expected', 'r') as f:
            expected = f.read()

        assert rendered == expected

        with open('msmtprc.jinja', 'r') as f:
            template = f.read()

        with open('msmtprc.autofix', 'r') as f:
            autofix = f.read()

        assert autofix == template
