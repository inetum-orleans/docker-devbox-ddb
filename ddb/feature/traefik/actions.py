# -*- coding: utf-8 -*-
import os
import shutil

from ddb.config import config
from ...action import Action


class TraefikInstalllCertsAction(Action):
    """
    Install generated certificates on traefik.
    """

    @property
    def event_bindings(self):
        return "certs:available"

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
        shutil.copy(private_key, private_key_filename_target)

        certificate_filename = "%s.crt" % (domain,)
        certificate_filename_target = os.path.join(certs_directory, certificate_filename)
        shutil.copy(certificate, certificate_filename_target)

        ssl_config_template = config.data.get('traefik.ssl_config_template') % (
            '/'.join([mapped_certs_directory, certificate_filename]),
            '/'.join([mapped_certs_directory, private_key_filename])
        )

        config_target = os.path.join(config_directory, "%s.ssl.toml" % (domain,))
        with open(config_target, "w") as config_file:
            config_file.write(ssl_config_template)
