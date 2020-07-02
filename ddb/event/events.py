from typing import Optional, Union

from ddb.binary import Binary as BinaryType
from . import event


# pylint:disable=redefined-outer-name

class File:
    """
    File related events.
    """

    @event("file:deleted")
    def deleted(self, file: str):
        """
        When a file is deleted.
        :param file:
        """

    @event("file:found")
    def found(self, file: str):
        """
        When a file is found.
        :param file:
        """

    @event("file:generated")
    def generated(self, source: Optional[str], target: str):
        """
        When a file is generated.
        :param source:
        :param target:
        """


class Certs:
    """
    Certificates related events.
    """

    @event("certs:generate")
    def generate(self, domain: str, wildcard: True):
        """
        Ask to generate a certificate.
        :param domain:
        :param wildcard:
        """

    @event("certs:remove")
    def remove(self, domain: str):
        """
        Ask to remove a certificate.
        :param domain:
        """

    @event("certs:generated")
    def generated(self, domain: str, wildcard: bool, private_key: Union[bytes, str], certificate: Union[bytes, str]):
        """
        When a certificate is generated.
        :param domain:
        :param wildcard:
        :param private_key:
        :param certificate:
        """

    @event("certs:removed")
    def removed(self, domain: str):
        """
        When a certificate is removed.
        :param domain:
        """

    @event("certs:available")
    def available(self, domain: str, wildcard: bool, private_key: Union[bytes, str], certificate: Union[bytes, str]):
        """
        When a certificate is available.
        :param domain:
        :param wildcard:
        :param private_key:
        :param certificate:
        :return:
        """


class Binary:
    """
    Binary related events.
    """

    @event("binary:unregistered")
    def unregistered(self, binary: BinaryType):
        """
        When a binary as been unregistered.
        :param binary:
        :return:
        """

    @event("binary:registered")
    def registered(self, binary: BinaryType):
        """
        When a binary has been registered.
        :param binary:
        :return:
        """

    @event("binary:found")
    def found(self, binary: BinaryType):
        """
        When a binary has been found.
        :param binary:
        """


class Run:
    """
    Run related events.
    """

    @event("run:run")
    def run(self, name: str):
        """
        When a command has been runned.
        :param name:
        """


class Docker:
    """
    Docker related events.
    """

    @event("docker:docker-compose-config")
    def docker_compose_config(self, docker_compose_config: dict):
        """
        When a docker compose configuration has been read.
        :param docker_compose_config:
        """

    @event("docker:docker-compose-before-events")
    def docker_compose_before_events(self, docker_compose_config: dict):
        """
        Before docker compose to emit events.
        :param docker_compose_config:
        """

    @event("docker:docker-compose-after-events")
    def docker_compose_after_events(self, docker_compose_config: dict):
        """
        After docker compose has emitted events.
        :param docker_compose_config:
        """

    @event("docker:binary")
    def binary(self, name=None, workdir=None, options=None, options_condition=None, args=None,
               docker_compose_service=None):
        """
        Ask a binary to be generated from docker compose service
        :param name:
        :param workdir:
        :param options:
        :param options_condition:
        :param args:
        :param docker_compose_service:
        :return:
        """


class Phase:
    """
    Phase related events.
    """

    @event("phase:init")
    def init(self):
        """
        Init phase
        """

    @event("phase:configure")
    def configure(self):
        """
        Configure phase
        """

    @event("phase:features")
    def features(self):
        """
        Features phase
        """

    @event("phase:config")
    def config(self):
        """
        Config phase
        """

    @event("phase:run")
    def run(self):
        """
        Run phase
        """


file = File()
certs = Certs()
binary = Binary()
run = Run()
docker = Docker()
phase = Phase()
