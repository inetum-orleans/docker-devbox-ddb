# -*- coding: utf-8 -*-
import os

import cfssl as cfssl_client

from .cfssl import checksums, writer
from ...action import Action
from ...config import config
from ...context import context
from ...event import events
from ...utils.file import force_remove, copy_if_different


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
    def execute(domain, wildcard=True):
        """
        Generate a certificate
        """
        if config.data.get('certs.type') == 'cfssl':
            GenerateCertAction.generate_cfssl(domain, wildcard)

    @staticmethod
    def generate_cfssl(domain, wildcard=True):
        """
        Generate domain certificate with CFSSL.
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
                                           config.data['certs.cfssl.append_ca_certificate'],
                                           client,
                                           config.data['certs.cfssl.verify_checksum'])

            context.log.success("TLS certificate generated for domain %s", domain)

            for generated_file in generated.values():
                events.file.generated(source=None, target=generated_file)

            private_key_path, certificate_path = generated['private_key'], generated['certificate']
            events.certs.generated(domain=domain, wildcard=wildcard, private_key=certificate_path,
                                   certificate=private_key_path)
        else:
            context.log.notice("TLS certificate exists for domain %s", domain)

        events.certs.available(domain=domain, wildcard=wildcard, private_key=private_key_path,
                               certificate=certificate_path)


class RemoveCertAction(Action):
    """
    Remove a certificate for a domain.
    """

    @property
    def event_bindings(self):
        return events.certs.remove

    @property
    def name(self) -> str:
        return "certs:remove"

    @staticmethod
    def execute(domain):
        """
        Remove certificate
        """
        if RemoveCertAction.remove_cfssl(domain):
            events.certs.removed(domain=domain)

    @staticmethod
    def remove_cfssl(domain):
        """
        Remove domain certificate generated with CFSSL.
        """
        certificate_path, private_key_path = writer.get_certs_path(domain,
                                                                   config.data['certs.cfssl.writer'],
                                                                   config.data['certs.destination'])

        removed = False
        if os.path.exists(certificate_path):
            force_remove(certificate_path)
            events.file.deleted(certificate_path)
            removed = True

        if os.path.exists(private_key_path):
            force_remove(private_key_path)
            events.file.deleted(certificate_path)
            removed = True

        return removed


class GenerateSignerCertificateAction(Action):
    """
    Generate the signer certificate, used to sign domains certificates.
    """

    @property
    def event_bindings(self):
        return events.certs.generated

    @property
    def name(self) -> str:
        return "certs:generate-signer"

    @property
    def disabled(self) -> bool:
        return config.data.get('certs.type') != 'cfssl'

    @staticmethod
    def execute(*args, **kwargs):
        """
        Generate certificate with CFSSL.
        """
        output = ".signer"
        certificate_path, _ = writer.get_certs_path(output,
                                                    config.data['certs.cfssl.writer'],
                                                    config.data['certs.destination'])

        if not os.path.exists(certificate_path):
            client_config = config.data.get('certs.cfssl.server')

            client = cfssl_client.CFSSL(**client_config)
            response = client.info('')

            destination = config.data['certs.destination']
            if not os.path.isdir(destination):
                os.makedirs(destination)

            generated = writer.write_files(response,
                                           output,
                                           None,
                                           None,
                                           config.data['certs.cfssl.writer'],
                                           config.data['certs.destination'],
                                           False,
                                           client,
                                           False)

            context.log.success("Signer TLS certificate generated")

            for generated_file in generated.values():
                events.file.generated(source=None, target=generated_file)
        else:
            context.log.notice("Signer TLS certificate exists")

        signer_destinations = config.data['certs.signer_destinations']
        if signer_destinations:
            certificate = os.path.join(config.data['certs.destination'],
                                       output + config.data['certs.cfssl.writer']['filenames']['certificate'] % '')

            for signer_destination in signer_destinations:
                dirname = os.path.dirname(signer_destination)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                if copy_if_different(certificate, signer_destination) or config.eject:
                    events.file.generated(source=certificate, target=signer_destination)
