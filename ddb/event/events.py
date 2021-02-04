from typing import Optional, Union, Iterable

from ddb.binary import Binary as BinaryType
from . import event
# pylint:disable=redefined-outer-name
from ..command import Command


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
    def generate(self, domain: str, wildcard=True):
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

    @event("run:command")
    def command(self, command: Iterable[str], system_path: bool = False):
        """
        When a command request should be handled.
        :param command:
        :param system_path:
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
    def binary(self, name=None, workdir=None, options=None, options_condition=None, condition=None, args=None,
               exe=False, entrypoint=None, global_=None, docker_compose_service=None):
        """
        Ask a binary to be generated from docker compose service
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

    @event("phase:download")
    def download(self):
        """
        Download phase
        """

    @event("phase:features")
    def features(self):
        """
        Features phase
        """

    @event("phase:info")
    def info(self):
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

    @event("phase:selfupdate")
    def selfupdate(self):
        """
        Selfupdate phase
        """


class Config:
    """
    Phase related events.
    """

    @event("config:reloaded")
    def reloaded(self):
        """
        Config has been reloaded
        """


class Main:
    """
    Main function related events.
    """

    @event("main:start")
    def start(self, command: Command):
        """
        Main start
        """

    @event("main:terminate")
    def terminate(self, command: Command):
        """
        Main terminate
        """

    @event("main:version")
    def version(self, silent: bool):
        """
        Main version
        """


file = File()
certs = Certs()
binary = Binary()
run = Run()
docker = Docker()
phase = Phase()
config = Config()
main = Main()
