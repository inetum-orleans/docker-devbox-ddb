from collections.abc import Iterable
from typing import Any

from ddb.binary import Binary as BinaryType

from ..command import Command
from . import event


class File:
    """
    File related events.
    """

    @event("file:deleted")
    def deleted(self, file: str) -> None:
        """
        When a file is deleted.

        :param file:
        """

    @event("file:found")
    def found(self, file: str) -> None:
        """
        When a file is found.

        :param file:
        """

    @event("file:generated")
    def generated(self, source: str | None, target: str) -> None:
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
    def generate(self, domain: str, *, wildcard: bool = True) -> None:
        """
        Ask to generate a certificate.

        :param domain:
        :param wildcard:
        """

    @event("certs:remove")
    def remove(self, domain: str) -> None:
        """
        Ask to remove a certificate.

        :param domain:
        """

    @event("certs:generated")
    def generated(self, domain: str, *, wildcard: bool, private_key: bytes | str, certificate: bytes | str) -> None:
        """
        When a certificate is generated.

        :param domain:
        :param wildcard:
        :param private_key:
        :param certificate:
        """

    @event("certs:removed")
    def removed(self, domain: str) -> None:
        """
        When a certificate is removed.

        :param domain:
        """

    @event("certs:available")
    def available(self, domain: str, *, wildcard: bool, private_key: bytes | str, certificate: bytes | str) -> None:
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
    def unregistered(self, binary: BinaryType) -> None:
        """
        When a binary as been unregistered.

        :param binary:
        :return:
        """

    @event("binary:registered")
    def registered(self, binary: BinaryType) -> None:
        """
        When a binary has been registered.

        :param binary:
        :return:
        """

    @event("binary:found")
    def found(self, binary: BinaryType) -> None:
        """
        When a binary has been found.

        :param binary:
        """


class Run:
    """
    Run related events.
    """

    @event("run:run")
    def run(self, name: str) -> None:
        """
        When a command has been runned.

        :param name:
        """

    @event("run:command")
    def command(self, command: Iterable[str], *, system_path: bool = False) -> None:
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
    def docker_compose_config(self, docker_compose_config: dict[str, Any]) -> None:
        """
        When a docker compose configuration has been read.

        :param docker_compose_config:
        """

    @event("docker:docker-compose-before-events")
    def docker_compose_before_events(self, docker_compose_config: dict[str, Any]) -> None:
        """
        Before docker compose to emit events.

        :param docker_compose_config:
        """

    @event("docker:docker-compose-after-events")
    def docker_compose_after_events(self, docker_compose_config: dict[str, Any]) -> None:
        """
        After docker compose has emitted events.

        :param docker_compose_config:
        """

    @event("docker:binary")
    def binary(
        self,
        name: str | None = None,
        workdir: str | None = None,
        options: str | None = None,
        options_condition: str | None = None,
        condition: str | None = None,
        args: str | None = None,
        *,
        exe: bool = False,
        entrypoint: str | None = None,
        global_: bool | None = None,
        docker_compose_service: str | None = None,
    ) -> None:
        """
        Ask a binary to be generated from docker compose service.
        """


class Phase:
    """
    Phase related events.
    """

    @event("phase:init")
    def init(self) -> None:
        """
        Init phase.
        """

    @event("phase:configure")
    def configure(self) -> None:
        """
        Configure phase.
        """

    @event("phase:download")
    def download(self) -> None:
        """
        Download phase.
        """

    @event("phase:features")
    def features(self) -> None:
        """
        Features phase.
        """

    @event("phase:info")
    def info(self) -> None:
        """
        Features phase.
        """

    @event("phase:config")
    def config(self) -> None:
        """
        Config phase.
        """

    @event("phase:run")
    def run(self) -> None:
        """
        Run phase.
        """

    @event("phase:selfupdate")
    def selfupdate(self) -> None:
        """
        Selfupdate phase.
        """


class Config:
    """
    Phase related events.
    """

    @event("config:reloaded")
    def reloaded(self) -> None:
        """
        Config has been reloaded.
        """


class Main:
    """
    Main function related events.
    """

    @event("main:start")
    def start(self, command: Command) -> None:
        """
        Main start.
        """

    @event("main:terminate")
    def terminate(self, command: Command) -> None:
        """
        Main terminate.
        """

    @event("main:version")
    def version(self, *, silent: bool) -> None:
        """
        Main version.
        """


file = File()
certs = Certs()
binary = Binary()
run = Run()
docker = Docker()
phase = Phase()
config = Config()
main = Main()
