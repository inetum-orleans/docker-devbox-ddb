from pathlib import Path
from typing import Any

import cfssl as cfssl_client

from ddb.action.action import EventBindings

from ...action import Action
from ...config import config
from ...context import context
from ...event import events
from ...utils.file import copy_if_different, force_remove
from .cfssl import checksums, writer


class GenerateCertAction(Action):
    """
    Generate a certificate for a domain.
    """

    @property
    def event_bindings(self) -> EventBindings:
        return events.certs.generate

    @property
    def name(self) -> str:
        return "certs:generate"

    @staticmethod
    def execute(domain: str, *, wildcard: bool = True) -> None:
        """
        Generate a certificate.
        """
        if config.data.get("certs.type") == "cfssl":
            GenerateCertAction.generate_cfssl(domain, wildcard=wildcard)

    @staticmethod
    def generate_cfssl(domain: str, *, wildcard: bool = True) -> None:
        """
        Generate domain certificate with CFSSL.
        """
        certificate_path, private_key_path = writer.get_certs_path(
            domain, config.data["certs.cfssl.writer"], config.data["certs.destination"]
        )
        if not Path(certificate_path).exists() or not Path(private_key_path).exists():
            client_config = config.data.get("certs.cfssl.server")

            client = cfssl_client.CFSSL(**client_config)

            certificate_request = cfssl_client.CertificateRequest()
            certificate_request.common_name = domain
            certificate_request.hosts = (domain, f"*.{domain}") if wildcard else domain

            response = client.new_cert(certificate_request)
            checksums.validate_checksums(response)

            destination = config.data["certs.destination"]
            Path(destination).mkdir(parents=True, exist_ok=True)

            generated = writer.write_files(
                response,
                domain,
                config.data["certs.cfssl.writer"],
                config.data["certs.destination"],
                append_ca_certificate=config.data["certs.cfssl.append_ca_certificate"],
                client=client,
                verify_checksum=config.data["certs.cfssl.verify_checksum"],
            )

            context.log.success("TLS certificate generated for domain %s", domain)

            for generated_file in generated.values():
                events.file.generated(source=None, target=generated_file)

            private_key_path, certificate_path = generated["private_key"], generated["certificate"]
            events.certs.generated(
                domain=domain, wildcard=wildcard, private_key=certificate_path, certificate=private_key_path
            )
        else:
            context.log.notice("TLS certificate exists for domain %s", domain)

        events.certs.available(
            domain=domain, wildcard=wildcard, private_key=private_key_path, certificate=certificate_path
        )


class RemoveCertAction(Action):
    """
    Remove a certificate for a domain.
    """

    @property
    def event_bindings(self) -> EventBindings:
        return events.certs.remove

    @property
    def name(self) -> str:
        return "certs:remove"

    @staticmethod
    def execute(domain: str) -> None:
        """
        Remove certificate.
        """
        if RemoveCertAction.remove_cfssl(domain):
            events.certs.removed(domain=domain)

    @staticmethod
    def remove_cfssl(domain: str) -> bool:
        """
        Remove domain certificate generated with CFSSL.
        """
        certificate_path, private_key_path = writer.get_certs_path(
            domain, config.data["certs.cfssl.writer"], config.data["certs.destination"]
        )

        removed = False
        if Path(certificate_path).exists():
            force_remove(certificate_path)
            events.file.deleted(certificate_path)
            removed = True

        if Path(private_key_path).exists():
            force_remove(private_key_path)
            events.file.deleted(certificate_path)
            removed = True

        return removed


class GenerateSignerCertificateAction(Action):
    """
    Generate the signer certificate, used to sign domains certificates.
    """

    @property
    def event_bindings(self) -> EventBindings:
        return events.certs.generated

    @property
    def name(self) -> str:
        return "certs:generate-signer"

    @property
    def disabled(self) -> bool:
        return bool(config.data.get("certs.type") != "cfssl")

    @staticmethod
    def execute(*args: Any, **kwargs: Any) -> None:
        """
        Generate certificate with CFSSL.
        """
        output = ".signer"
        certificate_path, _ = writer.get_certs_path(
            output, config.data["certs.cfssl.writer"], config.data["certs.destination"]
        )

        if not Path(certificate_path).exists():
            client_config = config.data.get("certs.cfssl.server")

            client = cfssl_client.CFSSL(**client_config)
            response = client.info("")

            destination = config.data["certs.destination"]
            Path(destination).mkdir(parents=True, exist_ok=True)

            generated = writer.write_files(
                response,
                output,
                config.data["certs.cfssl.writer"],
                config.data["certs.destination"],
                append_ca_certificate=False,
                client=client,
                verify_checksum=False,
            )

            context.log.success("Signer TLS certificate generated")

            for generated_file in generated.values():
                events.file.generated(source=None, target=generated_file)
        else:
            context.log.notice("Signer TLS certificate exists")

        signer_destinations = config.data["certs.signer_destinations"]
        if signer_destinations:
            certificate = str(
                Path(config.data["certs.destination"])
                / (output + config.data["certs.cfssl.writer"]["filenames"]["certificate"] % "")
            )

            for signer_destination in signer_destinations:
                Path(signer_destination).parent.mkdir(parents=True, exist_ok=True)
                if copy_if_different(certificate, signer_destination) or config.eject:
                    events.file.generated(source=certificate, target=signer_destination)
