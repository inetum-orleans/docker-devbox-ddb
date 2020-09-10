# -*- coding: utf-8 -*-
import os
from typing import Dict

from jinja2 import Template

from ddb.config import config
from ddb.feature.traefik.schema import ExtraServiceSchema
from ...action import Action
from ...context import context
from ...event import events
from ...utils.file import write_if_different, copy_if_different, force_remove


class TraefikInstalllCertsAction(Action):
    """
    Install generated certificates on traefik.
    """

    @property
    def event_bindings(self):
        return events.certs.available

    @property
    def name(self) -> str:
        return "traefik:install-certs"

    @staticmethod
    def execute(domain: str, private_key: str, certificate: str, wildcard: bool = False):
        """
        Execute action
        """
        certs_directory = config.data.get('traefik.certs_directory')
        mapped_certs_directory = config.data.get('traefik.mapped_certs_directory')
        config_directory = config.data.get('traefik.config_directory')

        private_key_filename = "%s.key" % (domain,)
        private_key_filename_target = os.path.join(certs_directory, private_key_filename)
        copy_if_different(private_key, private_key_filename_target, log=True)

        certificate_filename = "%s.crt" % (domain,)
        certificate_filename_target = os.path.join(certs_directory, certificate_filename)
        copy_if_different(certificate, certificate_filename_target, log=True)

        ssl_config_template = Template(config.data.get('traefik.ssl_config_template'))
        config_data = dict(config.data)
        config_data['_local'] = {
            'certFile': '/'.join([mapped_certs_directory, certificate_filename]),
            'keyFile': '/'.join([mapped_certs_directory, private_key_filename])
        }

        ssl_config = ssl_config_template.render(config_data)

        config_target = os.path.join(config_directory, "%s.ssl.toml" % (domain,))
        if write_if_different(config_target, ssl_config, 'r', 'w'):
            context.log.success("SSL Configuration file written for domain %s" % (domain,))
        else:
            context.log.notice("SSL Configuration file exists for domain %s" % (domain,))


class TraefikUninstalllCertsAction(Action):
    """
    Uninstall removed certificates from traefik.
    """

    @property
    def event_bindings(self):
        return events.certs.removed

    @property
    def name(self) -> str:
        return "traefik:uninstall-certs"

    @staticmethod
    def execute(domain: str):
        """
        Execute action
        """
        config_directory = config.data.get('traefik.config_directory')
        config_target = os.path.join(config_directory, "%s.ssl.toml" % (domain,))

        if os.path.exists(config_target):
            force_remove(config_target)
            context.log.notice("SSL Configuration file removed for domain %s" % (domain,))

        certs_directory = config.data.get('traefik.certs_directory')
        private_key_filename = "%s.key" % (domain,)
        private_key_filename_target = os.path.join(certs_directory, private_key_filename)
        if os.path.exists(private_key_filename_target):
            force_remove(private_key_filename_target)
            context.log.notice("SSL private key file removed for domain %s" % (domain,))

        certificate_filename = "%s.crt" % (domain,)
        certificate_filename_target = os.path.join(certs_directory, certificate_filename)
        if os.path.exists(certificate_filename_target):
            force_remove(certificate_filename_target)
            context.log.notice("SSL certificate file removed for domain %s" % (domain,))


class TraefikExtraServicesAction(Action):
    """
    Generates extra services configuration to register any http/https URL inside the traefik reverse proxy.
    """

    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def name(self) -> str:
        return "traefik:extra-services"

    @staticmethod
    def execute():
        """
        Execute action
        """
        config_directory = config.data.get('traefik.config_directory')
        config_template = Template(config.data.get('traefik.extra_services_config_template'))

        extra_services = config.data.get('traefik.extra_services')  # type: Dict[str, ExtraServiceSchema]
        if extra_services:
            for id_, extra_service in extra_services.items():
                data = dict(config.data)
                local_data = dict(extra_service)
                local_data['id'] = id_
                data['_local'] = local_data

                if local_data.get('domain'):
                    local_data['domain'] = Template(local_data.get('domain')).render(data)

                if local_data.get('rule'):
                    local_data['rule'] = Template(local_data.get('rule')).render(data)

                if local_data.get('url'):
                    local_data['url'] = Template(local_data.get('url')).render(data)

                rendered_config = config_template.render(data)

                if local_data.get('domain'):
                    prefix = local_data.get('domain')
                else:
                    prefix = '.'.join(
                        x for x in ['rule', config.data.get('core.domain.sub'), config.data.get('core.domain.ext')] if x
                    )

                config_target = os.path.join(config_directory, "%s.extra-service.%s.toml" % (prefix, id_))
                if write_if_different(config_target, rendered_config, 'r', 'w'):
                    context.log.success(
                        "Extra service configuration file written for domain %s" % (prefix,))
                else:
                    context.log.notice(
                        "Extra service configuration file exists for domain %s" % (prefix,))

                # TODO: Handle removal using cache
