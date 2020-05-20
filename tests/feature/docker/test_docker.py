import os

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.binary import binaries
from ddb.event import bus
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerFeature, EmitDockerComposeConfigAction
from ddb.utils.process import effective_command


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

        def listener(docker_compose_config):
            custom_event_listeners.append(docker_compose_config)

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

        def listener(data, docker_compose_service):
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

        def listener(data, docker_compose_service):
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
        assert {"args": ("emit-one-arg",), "kwargs": {"docker_compose_service": "docker"}} in some_events
        assert {"args": ("emit-one-arg-2",), "kwargs": {"docker_compose_service": "docker2"}} in some_events
        assert {"args": ("emit-some-arg",),
                "kwargs": {'image': 'ubuntu', 'kw1': 'emit-one-kwarg', 'kw2': 7, 'version': '3.7',
                           "docker_compose_service": "docker"}} in some_events

        assert len(another_events) == 2
        assert {"args": ("emit-another-arg",), "kwargs": {"docker_compose_service": "docker"}} in another_events
        assert {"args": (),
                "kwargs": {"kw1": "emit-another-kwarg", "docker_compose_service": "docker2"}} in another_events

    def test_binary_workdir(self, project_loader):
        project_loader("binary-workdir")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert len(list(binaries.all())) == 2
        assert binaries.has("npm")
        assert binaries.has("node")

    def test_binary_options(self, project_loader):
        project_loader("binary-options")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert len(list(binaries.all())) == 3
        assert binaries.has("npm-simple")
        assert binaries.has("npm-conditions")
        assert binaries.has("mysql")

        npm_simple = binaries.get("npm-simple")
        assert npm_simple.command() == (''.join(
            effective_command("docker-compose")) + " run --workdir=/app/. --label traefik.enable=false node").split()
        assert npm_simple.command("serve") == (''.join(
            effective_command("docker-compose")) + ' run --workdir=/app/. --label traefik.enable=false node').split()
        assert npm_simple.command("run serve") == (''.join(
            effective_command("docker-compose")) + ' run --workdir=/app/. --label traefik.enable=false node').split()

        npm_conditions = binaries.get("npm-conditions")
        assert npm_conditions.command() == (''.join(
            effective_command("docker-compose")) + " run --workdir=/app/. --label traefik.enable=false node").split()
        assert npm_conditions.command("serve") == (''.join(
            effective_command("docker-compose")) + ' run --workdir=/app/. --label traefik.enable=false node').split()
        assert npm_conditions.command("run serve") == (
                ''.join(effective_command("docker-compose")) + ' run --workdir=/app/. node').split()

        mysql = binaries.get("mysql")
        assert mysql.command() == (''.join(effective_command(
            "docker-compose")) + ' run --workdir=/app/. db mysql -hdb -uproject-management-tool -pproject-management-tool').split()

    def test_local_volume_simple(self, project_loader):
        project_loader("local-volume-simple")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert not os.path.exists('node-path')
        assert os.path.isdir('existing-directory')
        assert os.path.isdir('new_directory')
        assert os.path.isfile('existing-file.txt')
        assert os.path.isfile('new_file')
        assert os.path.isfile('another_new_file.txt')

        with open('existing-file.txt', 'r') as f:
            assert f.read() == 'existing-file.txt'

    def test_local_volume_related(self, project_loader):
        project_loader("local-volume-related")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = EmitDockerComposeConfigAction()
        action.execute()

        assert not os.path.exists('node-path')
        assert os.path.isdir('new_directory')
        assert os.path.isdir('child')
        assert os.path.isdir(os.path.join('new_directory', 'some', 'child'))
