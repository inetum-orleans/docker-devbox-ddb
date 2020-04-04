# -*- coding: utf-8 -*-
import os
from typing import Iterable, Union, Callable

import cfssl as cfssl_client

from .cfssl import checksums, writer
from ...action import Action
from ...config import config


class GenerateCertAction(Action):
    """
    Generate a certificate for a domain.
    """

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], Callable]]]:
        return "certs:generate"

    @property
    def name(self) -> str:
        return "certs:generate"

    def execute(self, domain, wildcard=True):
        if config.data.get('certs.type') == 'cfssl':
            GenerateCertAction.execute_cfssl(domain, wildcard)

    @staticmethod
    def execute_cfssl(domain, wildcard=True):
        """
        Generate CA certificate with CFSSL.
        """
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

        writer.write_files(response,
                           domain,
                           None,
                           None,
                           config.data['certs.cfssl.writer'],
                           config.data['certs.destination'],
                           False,
                           client,
                           False)
