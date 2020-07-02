# -*- coding: utf-8 -*-
import os

from ddb.config import config
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

        ssl_config_template = config.data.get('traefik.ssl_config_template') % (
            '/'.join([mapped_certs_directory, certificate_filename]),
            '/'.join([mapped_certs_directory, private_key_filename])
        )

        config_target = os.path.join(config_directory, "%s.ssl.toml" % (domain,))
        if write_if_different(config_target, ssl_config_template, 'r', 'w'):
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
