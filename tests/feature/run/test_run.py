from typing import Iterable

import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import load_registered_features, register_actions_in_event_bus
from ddb.binary import binaries, Binary
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.run import RunFeature, RunAction


class BinaryMock(Binary):
    def __init__(self, name, *command):
        self._name = name
        self._command = command

    def command(self, *args) -> Iterable[str]:
        return self._command

    @property
    def name(self) -> str:
        return self._name

    def is_same(self, binary) -> bool:
        return self.command() == binary.command()


class TestRunFeature:
    def test_empty_project_without_core(self, project_loader):
        project_loader("empty")

        features.register(RunFeature())
        load_registered_features()

        action = RunAction()
        action.execute()

    def test_empty_project_with_core(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()

        action = RunAction()
        action.execute()

    def test_run_missing_binary(self, project_loader):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()

        action = RunAction()

        with pytest.raises(ValueError):
            action.run("missing")

    def test_run_existing_binary(self, project_loader, capsys: CaptureFixture):
        project_loader("empty")

        features.register(CoreFeature())
        features.register(RunFeature())
        load_registered_features()
        register_actions_in_event_bus(True)

        binaries.register(BinaryMock("test", "some", "command"))

        action = RunAction()
        action.run("test")

        read = capsys.readouterr()

        assert read.out == "some command\n"
