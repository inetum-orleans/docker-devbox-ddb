# -*- coding: utf-8 -*-
import os
import re
from typing import Dict

from jinja2 import Template

from ddb.config import config
from ddb.feature.traefik.schema import ExtraServiceSchema
from ...action import Action, InitializableAction
from ...cache.removal import RemovalCacheSupport
from ...config.migrations import MigrationsDotty
from ...context import context
from ...event import events
from ...utils.file import write_if_different, copy_if_different, force_remove, FileUtils


def get_template(template: str) -> Template:
    """
    Retrieve the template object base on the input template string
    :param template: the template
    :return:
    """
    if re.compile('^(https?|file)://').match(template):
        return Template(FileUtils.get_file_content(template))
    return Template(template)


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

        config_data = dict(config.data)
        config_data['_local'] = {
            'certFile': '/'.join([mapped_certs_directory, certificate_filename]),
            'keyFile': '/'.join([mapped_certs_directory, private_key_filename])
        }

        ssl_config = get_template(config.data.get('traefik.ssl_config_template')).render(config_data)

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


class TraefikExtraServicesAction(InitializableAction):
    """
    Generates extra services configuration to register any http/https URL inside the traefik reverse proxy.
    """

    def __init__(self):
        super().__init__()
        self.removal_cache_support = None  # type: RemovalCacheSupport

    @property
    def event_bindings(self):
        return events.phase.configure

    @property
    def name(self) -> str:
        return "traefik:extra-services"

    def initialize(self):
        self.removal_cache_support = RemovalCacheSupport("traefik.extra-services", {'generated-files', 'certs-domains'})

    def destroy(self):
        if self.removal_cache_support:
            self.removal_cache_support.close()
            self.removal_cache_support = None

    @staticmethod
    def get_extra_services():
        """
        Get extra services defined in configuration
        """
        extra_services = config.data.get('traefik.extra_services')  # type: Dict[str, ExtraServiceSchema]
        if extra_services:
            for id_, extra_service in extra_services.items():
                extra_service_data, config_data = \
                    TraefikExtraServicesAction._prepare_extra_service_data(extra_service, id_)
                yield id_, extra_service_data, config_data

    def execute(self):
        """
        Execute action
        """
        self.removal_cache_support.prepare()

        config_directory = config.data.get('traefik.config_directory')
        config_template = get_template(config.data.get('traefik.extra_services_config_template'))

        for id_, extra_service_data, config_data in TraefikExtraServicesAction.get_extra_services():
            rendered_config = config_template.render(config_data)

            if extra_service_data.get('domain'):
                prefix = extra_service_data.get('domain')
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

            self.removal_cache_support.set_current_value('generated-files', config_target)

            if extra_service_data.get('https') is not False:
                events.certs.generate(extra_service_data['domain'])
                self.removal_cache_support.set_current_value('certs-domains', extra_service_data['domain'])

        for (key, value) in self.removal_cache_support.get_removed():
            if key == 'certs-domains':
                events.certs.remove(value)
            elif key == 'generated-files':
                force_remove(value)

    @staticmethod
    def _prepare_extra_service_data(extra_service, id_):
        data = MigrationsDotty(dict(config.data))
        extra_service_data = dict(extra_service)
        extra_service_data['id'] = id_
        data['_local'] = extra_service_data
        if extra_service_data.get('domain'):
            extra_service_data['domain'] = Template(extra_service_data.get('domain')).render(data)
        if extra_service_data.get('rule'):
            extra_service_data['rule'] = Template(extra_service_data.get('rule')).render(data)
        if extra_service_data.get('url'):
            extra_service_data['url'] = Template(extra_service_data.get('url')).render(data)

        if extra_service['https'] is not None:
            extra_service_data['redirect_to_https'] = False
        if extra_service_data.get('redirect_to_https'):
            extra_service['https'] = True
        if extra_service_data.get('redirect_to_https') is None and extra_service['https'] is None:
            extra_service_data['redirect_to_https'] = config.data.get('jsonnet.docker.virtualhost.redirect_to_https')

        if not extra_service_data.get('path_prefix'):
            extra_service_data['redirect_to_path_prefix'] = False
        if extra_service['redirect_to_path_prefix'] is None:
            extra_service_data['redirect_to_path_prefix'] = \
                config.data.get('jsonnet.docker.virtualhost.redirect_to_path_prefix')

        return extra_service_data, data
