import os
import re
from abc import ABC, abstractmethod

from _pytest.capture import CaptureFixture

from ddb.__main__ import main, load_registered_features
from ddb.config import config
from ddb.feature import features
from ddb.feature.core import CoreFeature
from ddb.feature.shell import ActivateAction, DeactivateAction, ShellFeature
from ddb.feature.shell.actions import encode_environ_backup, CreateAliasShim
from ddb.feature.shell.integrations import BashShellIntegration, ShellIntegration, CmdShellIntegration


class ActivateActionBase(ABC):
    @abstractmethod
    def build_shell_integration(self) -> ShellIntegration:
        pass

    @property
    @abstractmethod
    def export_regex(self):
        pass

    @abstractmethod
    def get_shim_filename(self, shimname: str) -> str:
        pass

    @property
    @abstractmethod
    def unset_regex(self):
        pass

    @property
    @abstractmethod
    def filepath_regex(self):
        pass

    @property
    def additional_environment_variable(self) -> dict:
        return {}

    def test_run(self, capsys: CaptureFixture):
        action = ActivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        env = dict(export_match)

        assert sorted(env.keys()) == sorted(
            ["DDB_PROJECT_HOME", "DDB_SHELL_ENVIRON_BACKUP"] + list(self.additional_environment_variable.keys()))

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

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        env = dict(export_match)

        assert sorted(env.keys()) == sorted(
            ["DDB_PROJECT_HOME", "DDB_SOME", "DDB_ANOTHER_DEEP",
             "DDB_SHELL_ENVIRON_BACKUP"] + list(self.additional_environment_variable.keys()))

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

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '')
        first = system_path.split(os.pathsep)[0]

        assert first == os.path.normpath(os.path.join(os.getcwd(), "./bin")) \
               or first == os.path.normpath(os.path.join(os.getcwd(), "./.bin"))

        os.environ.update(env)

        deactivate_action = DeactivateAction(self.build_shell_integration())
        deactivate_action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '').split(os.pathsep)
        first = system_path[0]

        assert first != os.path.normpath(os.path.join(os.getcwd(), "./bin")) or \
               first != os.path.normpath(os.path.join(os.getcwd(), "./.bin"))

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

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '').split(os.pathsep)
        last = system_path[-1]

        assert last == os.path.normpath(os.path.join(os.getcwd(), "./bin")) \
               or last == os.path.normpath(os.path.join(os.getcwd(), "./.bin"))

        os.environ.update(env)

        deactivate_action = DeactivateAction(self.build_shell_integration())
        deactivate_action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        env = dict(export_match)

        system_path = env.get('PATH', '').split(os.pathsep)
        last = system_path[-1]

        assert last != os.path.normpath(os.path.join(os.getcwd(), "./bin")) or \
               last != os.path.normpath(os.path.join(os.getcwd(), "./.bin"))

    def test_empty_project_main_aliases(self, project_loader):
        project_loader("aliases")

        main(["configure"])

        if os.name == 'nt':
            assert os.path.exists(os.path.join("bin", "dc.bat"))
            # TODO: Check the content of the file with an assertion, and test the feature behavior on windows
        else:
            assert os.path.exists(os.path.join("bin", "dc"))
            with open(os.path.join("bin", "dc"), 'r') as f:
                content = f.read()
                assert 'docker-compose "$@"' in content


class TestBashActivateAction(ActivateActionBase):
    export_regex = r"^export (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^/unset (.+)()$"
    filepath_regex = r"^(?:.* )?(.+)$"

    def build_shell_integration(self) -> ShellIntegration:
        return BashShellIntegration()

    def get_shim_filename(self, shimname: str) -> str:
        return shimname


class TestCmdActivateAction(ActivateActionBase):
    export_regex = r"^set (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^set (.+)=()$"
    filepath_regex = r"^(?:.* )?(.+)$"

    @property
    def additional_environment_variable(self) -> dict:
        return {'NL': '^'}

    def build_shell_integration(self) -> ShellIntegration:
        return CmdShellIntegration()

    def get_shim_filename(self, shimname: str) -> str:
        return "{}.bat".format(shimname)


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

    @property
    @abstractmethod
    def filepath_regex(self):
        pass

    @property
    def additional_environment_variable(self) -> dict:
        return {}

    def test_run(self, capsys: CaptureFixture):
        os.environ['DDB_SHELL_ENVIRON_BACKUP'] = encode_environ_backup(dict(os.environ))

        action = DeactivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        exported = dict(export_match)
        assert exported == self.additional_environment_variable

        unset_match = re.findall(self.unset_regex, script, re.MULTILINE)
        unset = dict(unset_match)
        assert len(unset) == 1
        assert 'DDB_SHELL_ENVIRON_BACKUP' in unset.keys()

    def test_run_with_empty_initial_env(self, capsys: CaptureFixture):
        expected_environ = dict()

        os.environ.clear()
        os.environ.update(expected_environ)
        os.environ['DDB_SHELL_ENVIRON_BACKUP'] = encode_environ_backup(expected_environ)

        action = DeactivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        exported = dict(export_match)
        assert exported == self.additional_environment_variable

        unset_match = re.findall(self.unset_regex, script, re.MULTILINE)
        unset = dict(unset_match)
        assert unset

        assert sorted(unset.keys()) == sorted(("DDB_SHELL_ENVIRON_BACKUP",))

    def test_run_with_changed_env_variable(self, capsys: CaptureFixture):
        expected_environ = {"DDB_CHANGE": "foo", "DDB_NO_CHANGE": "ok", "DDB_REMOVED": "removed"}

        os.environ.clear()
        os.environ.update(expected_environ)
        os.environ['DDB_SHELL_ENVIRON_BACKUP'] = encode_environ_backup(expected_environ)

        removed_item = os.environ.pop("DDB_REMOVED")
        os.environ["DDB_CHANGE"] = "bar"
        os.environ["DDB_ADDED"] = "added"

        action = DeactivateAction(self.build_shell_integration())
        action.execute()

        capture = capsys.readouterr()
        assert capture.out
        assert not capture.err

        filepath = re.match(self.filepath_regex, capture.out).group(1)
        with open(filepath, 'r', encoding='utf-8') as file:
            script = file.read()

        export_match = re.findall(self.export_regex, script, re.MULTILINE)
        exported = dict(export_match)
        assert len(exported) == (2 + len(self.additional_environment_variable.keys()))
        assert sorted(exported.keys()) == sorted(
            ["DDB_CHANGE", "DDB_REMOVED"] + list(self.additional_environment_variable.keys()))
        assert sorted(exported.values()) == sorted(
            ["foo", removed_item] + list(self.additional_environment_variable.values()))

        unset_match = re.findall(self.unset_regex, script, re.MULTILINE)
        unset = dict(unset_match)
        assert len(unset) == 2
        assert sorted(unset.keys()) == sorted(("DDB_SHELL_ENVIRON_BACKUP", "DDB_ADDED"))


class TestBashDeactivateAction(DeactivateActionBase):
    export_regex = r"^export (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^unset (.+)()$"
    filepath_regex = r"^(?:.* )?(.+)$"

    def build_shell_integration(self) -> ShellIntegration:
        return BashShellIntegration()


class TestCmdDeactivateAction(DeactivateActionBase):
    export_regex = r"^set (.+?)=[\'\"]?(.+?)[\'\"]?$"
    unset_regex = r"^set (.+)=()$"
    filepath_regex = r"^(?:.* )?(.+)$"

    @property
    def additional_environment_variable(self) -> dict:
        return {'NL': '^'}

    def build_shell_integration(self) -> ShellIntegration:
        return CmdShellIntegration()
