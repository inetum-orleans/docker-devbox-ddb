from ddb.__main__ import load_registered_features
from ddb.event import bus
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature, EmitDockerComposeConfigAction


class TestDockerFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(DockerFeature())
        load_registered_features()

        action = EmitDockerComposeConfigAction()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(DockerFeature())
        load_registered_features()

        action = EmitDockerComposeConfigAction()
        action.execute()

    def test_ubuntu(self, project_loader):
        project_loader("ubuntu")

        features.register(DockerFeature())
        load_registered_features()

        custom_event_listeners = []

        def listener(config):
            custom_event_listeners.append(config)

        bus.on("docker:docker-compose-config", listener)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert len(custom_event_listeners) == 1
        assert custom_event_listeners[0] == {"version": "3.7", "services": {"docker": {"image": "ubuntu"}}}
