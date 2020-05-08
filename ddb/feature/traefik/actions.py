# -*- coding: utf-8 -*-
import os

from ddb.config import config
from ...action import Action
from ...context import context
from ...event import events
from ...utils.file import write_if_different, copy_if_different


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
    def execute(domain: str, private_key: str, certificate: str, *args, **kwargs):
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
