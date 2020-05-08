# -*- coding: utf-8 -*-
import os

import cfssl as cfssl_client

from .cfssl import checksums, writer
from ...action import Action
from ...config import config
from ...context import context
from ...event import events


class GenerateCertAction(Action):
    """
    Generate a certificate for a domain.
    """

    @property
    def event_bindings(self):
        return events.certs.generate

    @property
    def name(self) -> str:
        return "certs:generate"

    @staticmethod
    def execute(domain, *args, wildcard=True, **kwargs):
        """
        Execute action
        """
        if config.data.get('certs.type') == 'cfssl':
            GenerateCertAction.execute_cfssl(domain, wildcard)

    @staticmethod
    def execute_cfssl(domain, wildcard=True):
        """
        Generate CA certificate with CFSSL.
        """
        certificate_path, private_key_path = writer.get_certs_path(domain,
                                                                   config.data['certs.cfssl.writer'],
                                                                   config.data['certs.destination'])
        if not os.path.exists(certificate_path) or not os.path.exists(private_key_path):
            client_config = config.data.get('certs.cfssl.server')

            client = cfssl_client.CFSSL(**client_config)

            certificate_request = cfssl_client.CertificateRequest()
            certificate_request.common_name = domain
            certificate_request.hosts = (domain, "*.%s" % domain) if wildcard else domain

            response = client.new_cert(certificate_request)
            checksums.validate_checksums(response)

            destination = config.data['certs.destination']
            if not os.path.isdir(destination):
                os.makedirs(destination)

            generated = writer.write_files(response,
                                           domain,
                                           None,
                                           None,
                                           config.data['certs.cfssl.writer'],
                                           config.data['certs.destination'],
                                           False,
                                           client,
                                           False)

            context.log.success("TLS certificates generated for domain %s", domain)

            for generated_file in generated.values():
                events.file.generated(source=None, target=generated_file)

            certificate_path, private_key_path = generated['private_key'], generated['certificate']
            events.certs.generated(domain=domain, wildcard=wildcard, private_key=certificate_path,
                                   certificate=private_key_path)
        else:
            context.log.notice("TLS certificates exists for domain %s", domain)

        events.certs.available(domain=domain, wildcard=wildcard, private_key=private_key_path,
                               certificate=certificate_path)
