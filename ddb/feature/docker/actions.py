# -*- coding: utf-8 -*-
import os
import re
from pathlib import PurePosixPath, Path
from typing import Union, Iterable

import yaml
from dotty_dict import Dotty
from simpleeval import simple_eval

from .binaries import DockerBinary
from ...action import Action
from ...action.action import EventBinding, InitializableAction
from ...binary import binaries
from ...cache import caches, register_project_cache
from ...config import config
from ...context import context
from ...event import bus, events
from ...utils.process import run


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
        self.binaries = dict()

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

    def before_events(self, docker_compose_config):
        """
        Reset current binaries dict.
        """
        self.binaries = dict()

    def after_events(self, docker_compose_config):
        """
        Cache binaries and remove binaries from cache that are not found in current config.
        """
        docker_binaries_cache = caches.get("docker.binaries")

        for name, binary in self.binaries.items():
            docker_binaries_cache.set(name, binary)

        binaries_to_remove = set()
        for name in docker_binaries_cache.keys():
            if name not in self.binaries.keys():
                unregistered_binary = binaries.unregister(name)
                events.binary.unregistered(binary=unregistered_binary)
                binaries_to_remove.add(name)

        for binary_to_remove in binaries_to_remove:
            docker_binaries_cache.pop(binary_to_remove)

        docker_binaries_cache.flush()

    def execute(self, name=None, workdir=None, options=None, options_condition=None, args=None, exe=False,
                docker_compose_service=None):
        """
        Execute action
        """
        if name is None and docker_compose_service:
            name = docker_compose_service
        if name is None:
            raise ValueError("name should be defined")

        binary = DockerBinary(name, docker_compose_service=docker_compose_service, workdir=workdir, options=options,
                              options_condition=options_condition, args=args, exe=exe)

        self.binaries[name] = binary

        if binaries.has(name):
            existing_binary = binaries.get(name)
            if existing_binary.is_same(binary):
                context.log.notice("Binary exists: %s" % (name,))
                events.binary.found(binary=binary)
                return

            binaries.unregister(name)

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
    def _create_local_volume(source, target):
        rel_source = os.path.relpath(source, ".")
        if os.path.exists(source):
            context.log.notice("Local volume source: %s (exists)", rel_source)
        else:
            _, source_ext = os.path.splitext(source)
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
        for service in docker_compose_config['services'].values():
            if 'volumes' not in service:
                continue

            for volume_spec in service['volumes']:
                if isinstance(volume_spec, dict):
                    source = volume_spec['source']
                    target = volume_spec['target']
                else:
                    source, target, _ = volume_spec.rsplit(':', 2)

                if source in external_volumes:
                    continue

                volume_mapping = (source, target)

                if volume_mapping not in volume_mappings:
                    volume_mappings.append(volume_mapping)
        return volume_mappings
