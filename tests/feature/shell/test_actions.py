import json
import os
import re
from abc import ABC, abstractmethod

from _pytest.capture import CaptureFixture

from ddb.__main__ import load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.shell import ActivateAction, DeactivateAction, ShellFeature
from ddb.feature.shell.integrations import BashShellIntegration, ShellIntegration, CmdShellIntegration


class ActivateActionBase(ABC):
    @abstractmethod
    def build_shell_integration(self) -> ShellIntegration:
        pass

    @property
    @abstractmethod
    def export_regex(self):
        pass

    @property
    @abstractmethod
    def unset_regex(self):
        pass

    def test_run(self, capsys: CaptureFixture):
        action = ActivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        env = dict(export_match)

        assert sorted(env.keys()) == sorted(("DDB_SHELL_ENVIRON_BACKUP",))

        assert "DDB_SHELL_ENVIRON_BACKUP" in env
        assert env["DDB_SHELL_ENVIRON_BACKUP"]

    def test_run_using_config(self, capsys: CaptureFixture):
        config.data["some"] = "testing"
        config.data["another.deep"] = "testing2"

        action = ActivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        env = dict(export_match)

        assert sorted(env.keys()) == sorted(("DDB_SOME", "DDB_ANOTHER_DEEP", "DDB_SHELL_ENVIRON_BACKUP"))

    def test_run_activate_deactivate_project(self, capsys: CaptureFixture, project_loader):
        project_loader("project")

        features.register(CoreFeature())
        features.register(ShellFeature())
        load_registered_features()

        action = ActivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '')
        first = system_path.split(os.pathsep)[0]

        assert first == os.path.normpath(os.path.join(os.getcwd(), "./bin"))

        os.environ.update(env)

        deactivate_action = DeactivateAction(self.build_shell_integration())
        deactivate_action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '')
        first = system_path.split(os.pathsep)[0]

        assert first != os.path.normpath(os.path.join(os.getcwd(), "./bin"))

    def test_run_activate_deactivate_project_prepend_false(self, capsys: CaptureFixture, project_loader):
        project_loader("project_prepend_false")

        features.register(CoreFeature())
        features.register(ShellFeature())
        load_registered_features()

        action = ActivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '')
        last = system_path.split(os.pathsep)[-1]

        assert last == os.path.normpath(os.path.join(os.getcwd(), "./bin"))

        os.environ.update(env)

        deactivate_action = DeactivateAction(self.build_shell_integration())
        deactivate_action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '')
        last = system_path.split(os.pathsep)[-1]

        assert last != os.path.normpath(os.path.join(os.getcwd(), "./bin"))


class TestBashActivateAction(ActivateActionBase):
    export_regex = r"^export (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^unset (.+)()$"

    def build_shell_integration(self) -> ShellIntegration:
        return BashShellIntegration()


class TestCmdActivateAction(ActivateActionBase):
    export_regex = r"^set (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^set (.+)=()$"

    def build_shell_integration(self) -> ShellIntegration:
        return CmdShellIntegration()


class DeactivateActionBase(ABC):
    @abstractmethod
    def build_shell_integration(self) -> ShellIntegration:
        pass

    @property
    @abstractmethod
    def export_regex(self):
        pass

    @property
    @abstractmethod
    def unset_regex(self):
        pass

    def test_run(self, capsys: CaptureFixture):
        os.environ['DDB_SHELL_ENVIRON_BACKUP'] = json.dumps(dict(os.environ))

        action = DeactivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        exported = dict(export_match)
        assert not exported

        unset_match = re.findall(self.unset_regex, capture.out, re.MULTILINE)
        unset = dict(unset_match)
        assert len(unset) == 1
        assert 'DDB_SHELL_ENVIRON_BACKUP' in unset.keys()

    def test_run_with_empty_initial_env(self, capsys: CaptureFixture):
        os.environ['DDB_SHELL_ENVIRON_BACKUP'] = json.dumps(dict())

        action = DeactivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        exported = dict(export_match)
        assert not exported

        unset_match = re.findall(self.unset_regex, capture.out, re.MULTILINE)
        unset = dict(unset_match)
        assert unset

        assert os.environ.keys() == unset.keys()

    def test_run_with_removed_env_variable(self, capsys: CaptureFixture):
        expected_environ = dict(os.environ)

        os.environ['DDB_SHELL_ENVIRON_BACKUP'] = json.dumps(expected_environ)

        removed_item = os.environ.popitem()

        action = DeactivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        export_match = re.findall(self.export_regex, capture.out, re.MULTILINE)
        exported = dict(export_match)
        assert len(exported) == 1
        assert list(exported.keys())[0] == removed_item[0]

        unset_match = re.findall(self.unset_regex, capture.out, re.MULTILINE)
        unset = dict(unset_match)
        assert len(unset) == 1
        assert 'DDB_SHELL_ENVIRON_BACKUP' in unset.keys()


class TestBashDeactivateAction(DeactivateActionBase):
    export_regex = r"^export (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^unset (.+)()$"

    def build_shell_integration(self) -> ShellIntegration:
        return BashShellIntegration()


class TestCmdDeactivateAction(DeactivateActionBase):
    export_regex = r"^set (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^set (.+)=()$"

    def build_shell_integration(self) -> ShellIntegration:
        return CmdShellIntegration()
