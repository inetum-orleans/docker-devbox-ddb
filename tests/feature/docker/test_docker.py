import os
import shutil

import pytest

from _pytest.capture import CaptureFixture
from compose.config.types import ServicePort
from dotty_dict import Dotty

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.action import actions
from ddb.binary import binaries
from ddb.binary.binary import DefaultBinary
from ddb.config import config
from ddb.event import bus
from ddb.feature import features
from ddb.feature.certs import CertsFeature
from ddb.feature.core import CoreFeature
from ddb.feature.docker import DockerDisplayInfoAction
from ddb.feature.docker import DockerFeature, EmitDockerComposeConfigAction
from ddb.feature.docker.binaries import DockerBinary
from ddb.feature.traefik import TraefikFeature
from ddb.utils.process import effective_command
from tests.utilstest import setup_cfssl


class TestDockerFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(DockerFeature())
        load_registered_features()

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(DockerFeature())
        load_registered_features()

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

    def test_ubuntu(self, project_loader):
        project_loader("ubuntu")

        features.register(DockerFeature())
        load_registered_features()

        custom_event_listeners = []

        def listener(docker_compose_config):
            custom_event_listeners.append(docker_compose_config)

        bus.on("docker:docker-compose-config", listener)

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

        assert len(custom_event_listeners) == 1
        assert custom_event_listeners[0] in [
            # docker-compose >= 1.27.0 returns major version only. see https://github.com/docker/compose/issues/7730
            {"version": "3", "services": {"docker": {"image": "ubuntu"}}},
            {"version": "3.7", "services": {"docker": {"image": "ubuntu"}}}
        ]

    def test_emit_one_arg(self, project_loader):
        project_loader("emit-one-arg")

        features.register(DockerFeature())
        load_registered_features()

        custom_event_listeners = []

        def listener(data):
            custom_event_listeners.append(data)

        bus.on("some:test", listener)

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
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

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
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

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

        assert len(some_events) == 3
        assert {"args": ("emit-one-arg",), "kwargs": {}} in some_events
        assert {"args": ("emit-one-arg-2",), "kwargs": {}} in some_events
        # docker-compose >= 1.27.0 returns major version only. see https://github.com/docker/compose/issues/7730
        assert {"args": ("emit-some-arg",),
                "kwargs": {'image': 'ubuntu', 'kw1': 'emit-one-kwarg', 'kw2': 7, 'version': '3.7'}} in some_events or \
               {"args": ("emit-some-arg",),
                "kwargs": {'image': 'ubuntu', 'kw1': 'emit-one-kwarg', 'kw2': 7, 'version': '3'}} in some_events

        assert len(another_events) == 2
        assert {"args": ("emit-another-arg",), "kwargs": {}} in another_events
        assert {"args": (),
                "kwargs": {"kw1": "emit-another-kwarg"}} in another_events

    def test_binary_workdir(self, project_loader):
        project_loader("binary-workdir")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

        assert len(list(binaries.all())) == 2
        assert binaries.has("npm")
        assert binaries.has("node")

    def test_binary_options(self, project_loader):
        project_loader("binary-options")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

        assert len(list(binaries.all())) == 3
        assert binaries.has("npm-simple")
        assert binaries.has("npm-conditions")
        assert binaries.has("mysql")

        npm_simple_set = binaries.get("npm-simple")
        assert len(npm_simple_set) == 1
        npm_simple = list(npm_simple_set)[0]
        assert npm_simple.command() == (''.join(
            effective_command(
                "docker-compose")) + " run --rm --workdir=/app/. --label traefik.enable=false node").split()
        assert npm_simple.command("serve") == (''.join(
            effective_command(
                "docker-compose")) + ' run --rm --workdir=/app/. --label traefik.enable=false node').split()
        assert npm_simple.command("run serve") == (''.join(
            effective_command(
                "docker-compose")) + ' run --rm --workdir=/app/. --label traefik.enable=false node').split()

        npm_conditions_set = binaries.get("npm-conditions")
        assert len(npm_conditions_set) == 1
        npm_conditions = list(npm_conditions_set)[0]
        assert npm_conditions.command() == (''.join(
            effective_command(
                "docker-compose")) + " run --rm --workdir=/app/. --label traefik.enable=false node").split()
        assert npm_conditions.command("serve") == (''.join(
            effective_command(
                "docker-compose")) + ' run --rm --workdir=/app/. --label traefik.enable=false node').split()
        assert npm_conditions.command("run serve") == (
                ''.join(effective_command("docker-compose")) + ' run --rm --workdir=/app/. node').split()

        mysql_set = binaries.get("mysql")
        assert len(mysql_set) == 1
        mysql = list(mysql_set)[0]
        assert mysql.command() == (''.join(effective_command(
            "docker-compose")) + ' run --rm --workdir=/app/. db mysql -hdb -uproject-management-tool -pproject-management-tool').split()

    def test_local_volume_simple(self, project_loader):
        project_loader("local-volume-simple")

        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
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

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

        assert not os.path.exists('node-path')
        assert os.path.isdir('new_directory')
        assert os.path.isdir('child')
        assert os.path.isdir(os.path.join('new_directory', 'some', 'child'))

    @pytest.mark.docker
    def test_traefik_cert(self, project_loader, module_scoped_container_getter):
        project_loader("traefik-cert")

        features.register(CertsFeature())
        features.register(TraefikFeature())
        features.register(DockerFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        setup_cfssl(module_scoped_container_getter)

        shutil.copyfile("docker-compose.yml", "docker-compose.original.yml")

        action = actions.get('docker:emit-docker-compose-config')  # type:EmitDockerComposeConfigAction
        action.execute()

        assert os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.key"))
        assert os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.crt"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.key"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.crt"))
        assert os.path.exists(os.path.join(config.paths.home, "traefik", "config", "web.domain.tld.ssl.toml"))

        shutil.copyfile("docker-compose.removed.yml", "docker-compose.yml")
        action.execute()

        assert not os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.key"))
        assert not os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.crt"))
        assert not os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.key"))
        assert not os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.crt"))
        assert not os.path.exists(os.path.join(config.paths.home, "traefik", "config", "web.domain.tld.ssl.toml"))

        shutil.copyfile("docker-compose.original.yml", "docker-compose.yml")
        action.execute()

        assert os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.key"))
        assert os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.crt"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.key"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.crt"))
        assert os.path.exists(os.path.join(config.paths.home, "traefik", "config", "web.domain.tld.ssl.toml"))

        shutil.copyfile("docker-compose.changed.yml", "docker-compose.yml")
        action.execute()

        assert not os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.key"))
        assert not os.path.exists(os.path.join(config.paths.project_home, ".certs", "web.domain.tld.crt"))
        assert not os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.key"))
        assert not os.path.exists(os.path.join(config.paths.home, "certs", "web.domain.tld.crt"))
        assert not os.path.exists(os.path.join(config.paths.home, "traefik", "config", "web.domain.tld.ssl.toml"))

        assert os.path.exists(os.path.join(config.paths.project_home, ".certs", "web-changed.domain.tld.key"))
        assert os.path.exists(os.path.join(config.paths.project_home, ".certs", "web-changed.domain.tld.crt"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "web-changed.domain.tld.key"))
        assert os.path.exists(os.path.join(config.paths.home, "certs", "web-changed.domain.tld.crt"))
        assert os.path.exists(os.path.join(config.paths.home, "traefik", "config", "web-changed.domain.tld.ssl.toml"))

class TestDockerDisplayInfoAction:

    def test_retrieve_environment_data(self):
        features.register(DockerFeature())
        load_registered_features()
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction

        assert {} == action._retrieve_environment_data(Dotty({}))
        assert {} == action._retrieve_environment_data(Dotty({'toto': 'toto'}))
        assert {'AZERTY': '123'} == action._retrieve_environment_data(Dotty({'environment': {'AZERTY': '123'}}))

    def test_retrieve_ports_data(self):
        features.register(DockerFeature())
        load_registered_features()
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction

        assert [] == action._retrieve_service_ports(Dotty({}))
        assert [] == action._retrieve_service_ports(Dotty({'toto': 'toto'}))
        assert [ServicePort(45, 123, None, None, None)] == action._retrieve_service_ports(
            Dotty({'ports': [{'published': '123', 'target': '45'}]}))
        assert [ServicePort(45, 123, None, None, None)] == action._retrieve_service_ports(Dotty({'ports': ['123:45']}))
        assert [ServicePort(45, 123, 'tcp', None, None)] == action._retrieve_service_ports(
            Dotty({'ports': ['123:45/tcp']}))

    def test_retrieve_binaries_data(self):
        features.register(DockerFeature())
        load_registered_features()
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction

        assert [] == action._retrieve_binaries_data(Dotty({}))
        assert [] == action._retrieve_binaries_data(Dotty({'toto': 'toto'}))
        assert [] == action._retrieve_binaries_data(Dotty({'labels': {'toto': '123'}}))
        assert ['npm-simple'] == action._retrieve_binaries_data(Dotty({'labels': {
            'ddb.emit.docker:binary[npm-simple](name)': 'npm-simple',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }}))
        assert ['npm', 'npm-simple'] == sorted(action._retrieve_binaries_data(Dotty({'labels': {
            'ddb.emit.docker:binary[npm](name)': 'npm',
            'ddb.emit.docker:binary[npm-simple](name)': 'npm-simple',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }})))

    def test_retrieve_vhosts_data(self):
        features.register(DockerFeature())
        load_registered_features()
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction

        assert [] == action._retrieve_vhosts_data(Dotty({}))
        assert [] == action._retrieve_vhosts_data(Dotty({'toto': 'toto'}))
        assert [] == action._retrieve_vhosts_data(Dotty({'labels': {'toto': '123'}}))
        assert ['http://web.domain.tld/'] == action._retrieve_vhosts_data(Dotty({'labels': {
            'traefik.http.routers.defaults-project.rule': 'Host(`web.domain.tld`)',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }}))
        assert ['http://test.tld/', 'http://web.domain.tld/'] == sorted(action._retrieve_vhosts_data(Dotty({'labels': {
            'traefik.http.routers.defaults-project.rule': 'Host(`web.domain.tld`)',
            'traefik.http.routers.test-project.rule': 'Host(`test.tld`)',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }})))
        assert ['http://test.tld/', 'https://web.domain.tld/'] == sorted(action._retrieve_vhosts_data(Dotty({'labels': {
            'traefik.http.routers.defaults-project.rule': 'Host(`web.domain.tld`)',
            'traefik.http.routers.defaults-project-tls.rule': 'Host(`web.domain.tld`)',
            'traefik.http.routers.test-project.rule': 'Host(`test.tld`)',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }})))

    def test_output_data(self, project_loader):
        features.register(DockerFeature())
        load_registered_features()
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction

        config.args.type = None

        assert '' == action._output_data('test', dict(), [], [], [])

        test_vhosts = action._retrieve_vhosts_data(Dotty({'labels': {
            'traefik.http.routers.defaults-project.rule': 'Host(`web.domain.tld`)',
            'traefik.http.routers.defaults-project-tls.rule': 'Host(`web.domain.tld`)',
            'traefik.http.routers.test-project.rule': 'Host(`test.tld`)',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }}))

        assert ('\n'.join(['+-------------------------+',
                           '| test                    |',
                           '+-------------------------+',
                           '| http://test.tld/        |',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+'])) == action._output_data('test', dict(), [],
                                                                                   [], test_vhosts)

        test_binaries = action._retrieve_binaries_data(Dotty({'labels': {
            'ddb.emit.docker:binary[npm](name)': 'npm',
            'ddb.emit.docker:binary[npm-simple](name)': 'npm-simple',
            'ddb.emit.docker:binary[npm-simple](workdir)': '/app'
        }}))

        assert ('\n'.join(['+-------------------------+',
                           '| test                    |',
                           '+-------------------------+',
                           '| npm                     |',
                           '| npm-simple              |',
                           '+-------------------------+',
                           '| http://test.tld/        |',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+'])) == action._output_data('test', dict(), [],
                                                                                   test_binaries, test_vhosts)

        test_envs = action._retrieve_environment_data(Dotty({'environment': {'AZERTY': '123'}}))
        assert ('\n'.join(['+-------------------------+',
                           '| test                    |',
                           '+-------------------------+',
                           '| AZERTY: 123             |',
                           '+-------------------------+',
                           '| npm                     |',
                           '| npm-simple              |',
                           '+-------------------------+',
                           '| http://test.tld/        |',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+'])) == action._output_data('test', test_envs, [],
                                                                                   test_binaries, test_vhosts)

        test_ports = action._retrieve_service_ports(Dotty({'ports': [{'published': '12123', 'target': '123'}]}))
        assert ('\n'.join(['+-------------------------+',
                           '| test                    |',
                           '+-------------------------+',
                           '| AZERTY: 123             |',
                           '+-------------------------+',
                           '| 12123:123/tcp           |',
                           '+-------------------------+',
                           '| npm                     |',
                           '| npm-simple              |',
                           '+-------------------------+',
                           '| http://test.tld/        |',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+'])) == action._output_data('test', test_envs, test_ports,
                                                                                   test_binaries, test_vhosts)

        config.args.type = 'nothing'
        assert '' == action._output_data('test', dict(), [], [], test_vhosts)

        config.args.type = 'vhost'
        assert ('\n'.join(['+-------------------------+',
                           '| test                    |',
                           '+-------------------------+',
                           '| http://test.tld/        |',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+'])) == action._output_data('test', dict(), [],
                                                                                   [], test_vhosts)

    def test_execute_traefik_cert(self, capsys: CaptureFixture, project_loader):
        project_loader("traefik-cert")

        features.register(DockerFeature())
        load_registered_features()
        config.args.type = None
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err
        assert ('\n'.join(['+-------------------------+',
                           '| web                     |',
                           '+-------------------------+',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+',
                           '\n'])) == capture.out

    def test_execute_extra_services(self, capsys: CaptureFixture, project_loader):
        project_loader("extra-services")

        features.register(DockerFeature())
        features.register(TraefikFeature())
        load_registered_features()
        config.args.type = None
        action = actions.get('docker:display-info')  # type:DockerDisplayInfoAction
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err
        assert ('\n'.join(['+-------------------------+',
                           '| web                     |',
                           '+-------------------------+',
                           '| https://web.domain.tld/ |',
                           '+-------------------------+',
                           '',
                           '+-----------------------------------------------+',
                           '| foo (extra)                                   |',
                           '+-----------------------------------------------+',
                           '| https://sub.test --> http://192.168.99.1:8080 |',
                           '+-----------------------------------------------+',
                           '\n'])) == capture.out


class TestDockerBinary:
    def test_docker_binary_compare_ne(self):
        binary1 = DockerBinary("npm", "node1")
        binary2 = DockerBinary("npm", "node2")
        binary3 = DockerBinary("npm", "node3")
        binary4 = DockerBinary("npm", "node4")

        assert binary1 != binary2 != binary3 != binary4
        assert hash(binary1) != hash(binary2) != hash(binary3) != hash(binary4)

    def test_docker_binary_compare_eq(self):
        binary1 = DockerBinary("npm", "node")
        binary2 = DockerBinary("npm", "node")

        assert binary1 == binary2
        assert hash(binary1) == hash(binary2)

    def test_docker_binary_sort(self):
        binary1 = DockerBinary("npm", "node1")
        binary2 = DockerBinary("npm", "node2")
        binary3 = DefaultBinary("npm", ["npm"])
        binary4 = DockerBinary("npm", "node4")

        bins = (binary1, binary2, binary3, binary4)
        sorted_bins = tuple(sorted(bins))
        expected = (binary1, binary2, binary4, binary3)

        assert sorted_bins == expected

        binary_with_condition = DockerBinary("npm", "node5", condition="some-condition")

        bins = (binary1, binary2, binary_with_condition, binary3, binary4)
        sorted_bins = tuple(sorted(bins))
        expected = (binary_with_condition, binary1, binary2, binary4, binary3)

        assert sorted_bins == expected
