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

    def test_emit_one_arg(self, project_loader):
        project_loader("emit-one-arg")

        features.register(DockerFeature())
        load_registered_features()

        custom_event_listeners = []

        def listener(data):
            custom_event_listeners.append(data)

        bus.on("some:test", listener)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert len(custom_event_listeners) == 1
        assert custom_event_listeners[0] == "emit-one-arg"

    def test_emit_one_arg_eval(self, project_loader):
        project_loader("emit-one-arg-eval")

        features.register(DockerFeature())
        load_registered_features()

        custom_event_listeners = []

        def listener(data):
            custom_event_listeners.append(data)

        bus.on("some:test", listener)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert len(custom_event_listeners) == 1
        assert custom_event_listeners[0] == 3

    def test_emit_complex(self, project_loader):
        project_loader("emit-complex")

        features.register(DockerFeature())
        load_registered_features()

        some_events = []
        another_events = []

        def someListener(*args, **kwargs):
            some_events.append({"args": args, "kwargs": kwargs})

        def anotherListener(*args, **kwargs):
            another_events.append({"args": args, "kwargs": kwargs})

        bus.on("some:test", someListener)
        bus.on("another:test", anotherListener)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert len(some_events) == 3
        assert {"args": ("emit-one-arg",), "kwargs": {}} in some_events
        assert {"args": ("emit-one-arg-2",), "kwargs": {}} in some_events
        assert {"args": ("emit-some-arg",),
                "kwargs": {'image': 'ubuntu', 'kw1': 'emit-one-kwarg', 'kw2': 7, 'version': '3.7'}} in some_events

        assert len(another_events) == 2
        assert {"args": ("emit-another-arg",), "kwargs": {}} in another_events
        assert {"args": (), "kwargs": {"kw1": "emit-another-kwarg"}} in another_events
