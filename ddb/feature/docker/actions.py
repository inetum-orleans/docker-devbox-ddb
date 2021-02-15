# -*- coding: utf-8 -*-
import keyword
import os
import re
from pathlib import PurePosixPath, Path
from typing import Union, Iterable, List, Dict, Set

import yaml
from dotty_dict import Dotty
from ddb.utils.simpleeval import simple_eval

from ddb.feature import features
from ddb.feature.traefik import TraefikExtraServicesAction
from .binaries import DockerBinary
from .lib.compose.config.types import ServicePort
from ...action import Action
from ...action.action import EventBinding, InitializableAction
from ...binary import binaries, Binary
from ...cache import caches, register_project_cache
from ...config import config
from ...context import context
from ...event import bus, events
from ...utils.process import run
from ...utils.table_display import get_table_display


class EmitDockerComposeConfigAction(Action):
    """
    Emit docker:docker-compose-config event with docker compose configuration,
    and events from ddb.event.bus.emit.<event-name>=prop1=prop1_value;prop2=int(prop2_value) labels.
    To generate multiple events of same name in the same service, event-name can be suffixed with "[xxx]".
    """

    def __init__(self):
        super().__init__()
        self.current_yaml_output = None
        self.key_re = re.compile(r"^\s*ddb\.emit\.(.+?)(?:\[(.+?)\])?(?:\((.+?)\))?\s*$")
        self.eval_re = re.compile(r"^\s*eval\((.*)\)\s*$")
        self._cert_domains_cache = register_project_cache("docker.cert-domains")

    @property
    def event_bindings(self):
        return (
            # TODO: Add support for custom docker-compose -f option (custom filename and multiple files)
            EventBinding(events.file.found,
                         processor=lambda file: ((), {}) if file == "docker-compose.yml" else False),
            EventBinding(events.file.generated,
                         processor=lambda source, target: ((), {}) if target == "docker-compose.yml" else False)
        )

    @property
    def name(self) -> str:
        return "docker:emit-docker-compose-config"

    def execute(self):
        """
        Execute action
        """
        if not os.path.exists("docker-compose.yml"):
            return

        yaml_output = run("docker-compose", "config")

        parsed_config = yaml.load(yaml_output, yaml.SafeLoader)
        docker_compose_config = Dotty(parsed_config)

        if self.current_yaml_output == yaml_output:
            return
        self.current_yaml_output = yaml_output

        events.docker.docker_compose_config(docker_compose_config=docker_compose_config)

        services = docker_compose_config.get('services')
        if not services:
            return

        events.docker.docker_compose_before_events(docker_compose_config=docker_compose_config)

        cert_domains = []

        def on_available(domain: str, wildcard: bool, private_key: Union[bytes, str], certificate: Union[bytes, str]):
            """
            When a certificate is available.
            :param domain:
            :param wildcard:
            :param private_key:
            :param certificate:
            :return:
            """
            cert_domains.append(domain)

        off = bus.on("certs:available", on_available)
        try:
            self._parse_docker_compose(docker_compose_config, services)
        finally:
            off()

        self._update_cache_and_emit_certs_remove(cert_domains)

        events.docker.docker_compose_after_events(docker_compose_config=docker_compose_config)

    def _parse_docker_compose(self, docker_compose_config: dict, services):
        for service_name, service in services.items():
            labels = service.get('labels')
            if not labels:
                continue

            if not isinstance(labels, dict):
                labels = {label.split("=", 1) for label in labels}

            event_data = self._build_event_data(docker_compose_config, labels, service, service_name)

            for (event_name, event_parsed_values) in event_data.items():
                for _, (args, kwargs) in event_parsed_values.items():
                    bus.emit(event_name, *args, **kwargs)

    def _update_cache_and_emit_certs_remove(self, cert_domains: Iterable[str]):
        removed_domains = []
        for previous_cert_domain in self._cert_domains_cache.keys():
            if previous_cert_domain not in cert_domains:
                events.certs.remove(previous_cert_domain)
                removed_domains.append(previous_cert_domain)

        for removed_domain in removed_domains:
            self._cert_domains_cache.pop(removed_domain)

        for cert_domain in cert_domains:
            self._cert_domains_cache.set(cert_domain, None)

    def _build_event_data(self, docker_compose_config, labels, service, service_name):  # pylint:disable=too-many-locals
        parsed_values = {}
        for key, value in labels.items():
            match = self.key_re.match(key)
            if not match:
                continue

            event_name = match.group(1)
            event_id = match.group(2)
            property_name = match.group(3)

            if property_name and property_name in keyword.kwlist:
                property_name = property_name + '_'

            args, kwargs = self._parse_value(value,
                                             {"service": service, "config": docker_compose_config},
                                             property_name)
            if event_name == 'docker:binary':
                kwargs["docker_compose_service"] = service_name

            event_parsed_values = parsed_values.get(event_name)
            if not event_parsed_values:
                event_parsed_values = dict()
                parsed_values[event_name] = event_parsed_values

            if event_id in event_parsed_values:
                event_args, event_kwargs = event_parsed_values[event_id]
                event_args.extend(args)
                event_kwargs.update(kwargs)
            else:
                event_parsed_values[event_id] = args, kwargs
        return parsed_values

    def _parse_value(self, value, names, property_name=None):
        values = map(str.strip, value.split("|")) if not property_name else [value]

        args = []
        kwargs = {}

        for expression in values:
            if not property_name and "=" in expression:
                var, val = expression.split("=", 1)
            else:
                var, val = property_name, expression

            eval_match = self.eval_re.match(val)
            if eval_match:
                val = simple_eval(eval_match.group(1), names=names)

            if var:
                kwargs[var] = val
            else:
                args.append(val)

        return args, kwargs


class DockerComposeBinaryAction(InitializableAction):
    """
    Convert ddb.event.bus.emit.docker:binary events to binary available from shell.
    """

    def __init__(self):
        super().__init__()
        self.binaries = set()  # type: Set[Binary]

    @property
    def event_bindings(self):
        return (events.docker.binary,
                EventBinding(events.docker.docker_compose_before_events, call=self.before_events),
                EventBinding(events.docker.docker_compose_after_events, call=self.after_events))

    @property
    def name(self) -> str:
        return "docker:docker-compose-binary"

    def initialize(self):
        register_project_cache("docker.binaries")

    def destroy(self):
        if caches.has("docker.binaries"):
            caches.unregister("docker.binaries", callback=lambda c: c.close())

    def before_events(self, docker_compose_config):
        """
        Reset current binaries dict.
        """
        self.binaries = set()

    def after_events(self, docker_compose_config):
        """
        Cache binaries and emit unregistered events for those removed from the previous run.
        """
        docker_binaries_cache = caches.get("docker.binaries")
        cached_binaries = docker_binaries_cache.get("cached_binaries")  # type: Set[Binary]
        if cached_binaries is None:
            cached_binaries = set()

        to_remove_binaries = set()
        for cached_binary in cached_binaries:
            if cached_binary not in self.binaries:
                if binaries.unregister(cached_binary.name, cached_binary):
                    events.binary.unregistered(binary=cached_binary)
                    to_remove_binaries.add(cached_binary)

        for to_remove in to_remove_binaries:
            cached_binaries.remove(to_remove)

        for binary in self.binaries:
            cached_binaries.add(binary)

        docker_binaries_cache.set("cached_binaries", cached_binaries)
        docker_binaries_cache.flush()

    def execute(self, name=None, workdir=None, options=None, options_condition=None, condition=None, args=None,
                exe=False, entrypoint=None, global_=None, docker_compose_service=None):
        """
        Execute action
        """
        if name is None and docker_compose_service:
            name = docker_compose_service
        if name is None:
            raise ValueError("name should be defined")

        binary = DockerBinary(name, docker_compose_service=docker_compose_service, workdir=workdir, options=options,
                              options_condition=options_condition, condition=condition, args=args, exe=exe,
                              entrypoint=entrypoint, global_=global_)

        self.binaries.add(binary)

        if binaries.has(name, binary):
            context.log.notice("Binary exists: %s" % (name,))
            events.binary.found(binary=binary)
            return

        binaries.register(binary)
        context.log.success("Binary registered: %s", name)
        events.binary.registered(binary=binary)


class LocalVolumesAction(Action):
    """
    This should avoid issues where docker creates local volume mount points as root:root.
    We can create those folder before starting the stack with the user account.
    """

    @property
    def event_bindings(self):
        return events.docker.docker_compose_config

    @property
    def name(self) -> str:
        return "docker:docker-compose-local-volumes"

    def execute(self, docker_compose_config: dict):
        """
        Execute action
        """
        if 'services' not in docker_compose_config:
            return

        external_volumes = docker_compose_config['volumes'].keys() if 'volumes' in docker_compose_config else []

        volume_mappings = self._get_volume_mappings(docker_compose_config, external_volumes)

        volume_mappings = [(source, target) for (source, target) in volume_mappings if
                           self._check_file_in_project(source)]

        for source, target in volume_mappings:
            self._create_local_volume(source, target)

        for source_a, destination_a in volume_mappings:
            for source_b, destination_b in volume_mappings:
                if source_a == source_b and destination_a == destination_b:
                    continue

                if destination_b.startswith(destination_a):
                    relative_destination = PurePosixPath(destination_b).relative_to(destination_a)
                    related_path = str(PurePosixPath().joinpath(source_a, relative_destination))
                    rel_related_path = os.path.relpath(os.path.normpath(str(related_path)), ".")

                    if not os.path.exists(rel_related_path):
                        os.makedirs(rel_related_path)
                        context.log.info("Local volume source: %s (related directory created)", rel_related_path)

                    self._fix_owner(rel_related_path)

    @staticmethod
    def _fix_owner(relative_path):
        if hasattr(os, 'chown'):
            stat_info = os.stat(relative_path)
            uid = stat_info.st_uid
            gid = stat_info.st_gid
            if uid != config.data.get("docker.user.uid") and gid != config.data.get("docker.user.gid"):
                context.log.warning("Invalid owner detected for %s", relative_path)
                try:
                    # pylint:disable=no-member
                    os.chown(relative_path, config.data.get("docker.user.uid"), config.data.get("docker.user.gid"))
                    context.log.info("Owner has been fixed for %s", relative_path)
                except OSError:
                    context.log.error("Run this command to fix: sudo chown -R \"%s:%s\" %s",
                                      config.data.get("docker.user.uid"), config.data.get("docker.user.gid"),
                                      relative_path)

    @staticmethod
    def _check_file_in_project(target):
        target_path = os.path.realpath(target)
        cwd = os.path.realpath(".")
        return target_path.startswith(cwd)

    @staticmethod
    def _create_local_volume(source, target):
        rel_source = os.path.relpath(source, ".")
        if os.path.exists(source):
            context.log.notice("Local volume source: %s (exists)", rel_source)
        else:
            _, source_ext = os.path.splitext(source)
            target_ext = None
            if target:
                _, target_ext = os.path.splitext(target)
            if source_ext or target_ext:
                # Create empty file, because with have an extension in source or target.
                os.makedirs(str(Path(source).parent), exist_ok=True)
                context.log.info("Local volume source: %s (file created)", rel_source)
                with open(source, "w"):
                    pass
                events.file.generated(source=None, target=rel_source)
            else:
                # Create empty directory, because neither source or target has an extension.
                os.makedirs(source)
                context.log.info("Local volume source: %s (directory created)", rel_source)
        LocalVolumesAction._fix_owner(rel_source)

    @staticmethod
    def _get_volume_mappings(docker_compose_config, external_volumes):
        volume_mappings = []
        external_volumes_dict = {}

        for service in docker_compose_config.get('services', {}).values():
            if 'volumes' not in service:
                continue

            for volume_spec in service['volumes']:
                if isinstance(volume_spec, dict):
                    source = volume_spec['source']
                    target = volume_spec['target']
                else:
                    source, target, _ = volume_spec.rsplit(':', 2)

                if source in external_volumes:
                    external_volumes_dict[source] = target
                    continue

                volume_mapping = (source, target)

                if volume_mapping not in volume_mappings:
                    volume_mappings.append(volume_mapping)

        for volume, volume_config in docker_compose_config.get('volumes', {}).items():
            if volume_config and volume_config.get('driver') == 'local' and volume_config.get('driver_opts'):
                driver_opts = volume_config.get('driver_opts')
                device = driver_opts.get('device')
                if device and driver_opts.get('o') == 'bind':
                    source = PurePosixPath(device).joinpath(volume)
                    target = external_volumes_dict.get(volume)
                    if source and target:
                        volume_mapping = (source, target)
                        if volume_mapping not in volume_mappings:
                            volume_mappings.append(volume_mapping)

        return volume_mappings


class DockerDisplayInfoAction(Action):
    """
    Retrieve exposed ports and vhosts from docker-compose config and display them to the user
    """

    def __init__(self):
        super().__init__()
        self.current_yaml_output = None

    @property
    def event_bindings(self):
        return (
            events.phase.info
        )

    @property
    def name(self) -> str:
        return "docker:display-info"

    def execute(self):
        """
        Execute action
        """
        if not os.path.exists("docker-compose.yml"):
            return

        yaml_output = run("docker-compose", "config")

        parsed_config = yaml.load(yaml_output, yaml.SafeLoader)
        docker_compose_config = Dotty(parsed_config)

        if self.current_yaml_output == yaml_output:
            return
        self.current_yaml_output = yaml_output

        services = docker_compose_config.get('services')
        if not services:
            return

        for service_name in sorted(services.keys()):
            service_config = services.get(service_name)
            environments = self._retrieve_environment_data(service_config)
            ports = self._retrieve_service_ports(service_config)
            docker_binaries = self._retrieve_binaries_data(service_config)
            vhosts = self._retrieve_vhosts_data(service_config)

            output = self._output_data(service_name, environments, ports, docker_binaries, vhosts)
            if output:
                print(output)
                print()

        if features.has('traefik'):
            for id_, extra_service_data, _ in TraefikExtraServicesAction.get_extra_services():
                output = self._output_traefik_data(id_, extra_service_data)
                print(output)
                print()

    @staticmethod
    def _retrieve_environment_data(service_config: Dotty) -> Dict[str, str]:
        """
        Retrieve environment data
        :param service_config: the service configuration
        :return: a dict containing environment variables
        """
        environments = service_config.get('environment')
        if not environments:
            return {}

        return environments

    @staticmethod
    def _retrieve_service_ports(service_config: Dotty) -> List[ServicePort]:  # pylint: disable=no-self-use
        """
        Retrieve services ports data
        :param service_config: the service configuration
        :return: a list of service port
        """
        ports = service_config.get('ports')
        if not ports:
            return []

        def _to_service_ports(port):
            if isinstance(port, str):
                return ServicePort.parse(port)

            parameters = {'target': None, 'published': None, 'protocol': None, 'mode': None, 'external_ip': None}
            parameters.update(port)
            return [ServicePort(**parameters)]

        service_ports = []
        for port in ports:
            for service_port in _to_service_ports(port):
                service_ports.append(service_port)

        return service_ports

    @staticmethod
    def _retrieve_binaries_data(service_config: Dotty) -> List[str]:  # pylint: disable=no-self-use
        """
        Retrieve binaries data
        :param service_config: the service configuration
        :return: a list containing binaries
        """
        labels = service_config.get('labels')
        if not labels:
            return []

        binary_regex_re = re.compile(r"^\s*ddb\.emit\.(.+?)(?:\[(.+?)\])?(?:\((.+?)\))?\s*$")

        binaries_labels = []
        for key in labels.keys():
            match = binary_regex_re.match(key)
            if not match:
                continue
            event_name = match.group(1)
            binary_name = match.group(2)
            if event_name == 'docker:binary' and binary_name not in binaries_labels:
                binaries_labels.append(match.group(2))

        return binaries_labels

    @staticmethod
    def _retrieve_vhosts_data(service_config: Dotty) -> List[str]:  # pylint: disable=no-self-use
        """
        Retrieve vhosts data
        :param service_config: the service configuration
        :return: a list containing vhosts data
        """
        labels = service_config.get('labels')
        if not labels:
            return []

        vhosts_regex_re = re.compile(r"^Host\(`(.+?)`\)$")

        vhosts_labels = []
        for key in labels.keys():
            value = labels.get(key)
            match = vhosts_regex_re.match(value)
            if not match:
                continue
            http_url = 'http://{}/'.format(match.group(1))
            https_url = 'https://{}/'.format(match.group(1))

            if '-tls.' in key:
                try:
                    vhosts_labels.remove(http_url)
                except ValueError:
                    pass
                vhosts_labels.append(https_url)
                continue

            if https_url not in vhosts_labels:
                vhosts_labels.append(http_url)

        return vhosts_labels

    @staticmethod
    def _output_data(service_name: str, environments: Dict[str, str],  # pylint: disable=no-self-use
                     ports: List[ServicePort], docker_binaries: List[str], vhosts: List[str]):
        """
        Process the data and render it to the user
        :param service_name: the service name
        :param environments: the service environment data to display
        :param ports: the service ports data to display
        :param docker_binaries: the list of docker binaries
        :param vhosts: the list of vhosts
        :return: a dict containing useful labels data
        """

        header_block = ['{}'.format(service_name)]
        blocks = [header_block]

        if (config.args.type is None or 'env' in config.args.type) and environments:
            tmp_content = []
            for key in sorted(environments.keys()):
                tmp_content.append('{}: {}'.format(key, environments.get(key)))

            blocks.append(tmp_content)

        if (config.args.type is None or 'port' in config.args.type) and ports:
            tmp_content = []
            for port in ports:
                tmp_content.append(port.legacy_repr() if
                                   hasattr(port, 'legacy_repr') else
                                   "%s:%s" % (port.published, port.target))
            blocks.append(tmp_content)

        if (config.args.type is None or 'bin' in config.args.type) and docker_binaries:
            tmp_content = []
            for binary in sorted(docker_binaries):
                tmp_content.append(binary)
            blocks.append(tmp_content)

        if (config.args.type is None or 'vhost' in config.args.type) and vhosts:
            tmp_content = []
            for vhost in sorted(vhosts):
                tmp_content.append(vhost)
            blocks.append(tmp_content)

        if blocks != [header_block]:
            return get_table_display(blocks, False)
        return ''

    @staticmethod
    def _output_traefik_data(id_, extra_service_data):
        if 'domain' in extra_service_data:
            domain = extra_service_data.get('domain')
            if extra_service_data.get('https') in [None, True]:
                domain = 'https://' + domain
            else:
                domain = 'http://' + domain
        else:
            domain = extra_service_data.get('rule')

        blocks = [
            [id_ + " (extra)"],
            [domain + ' --> ' + extra_service_data.get('url')]
        ]
        return get_table_display(blocks, False)
