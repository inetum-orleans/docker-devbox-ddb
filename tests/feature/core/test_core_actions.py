import re
import sys
from pathlib import Path

import pytest
import requests
from _pytest.capture import CaptureFixture
from pytest_mock import MockerFixture

from ddb import __version__
from ddb.cache import caches
from ddb.config import config
from ddb.context import context
from ddb.feature.core.actions import (
    CheckForUpdateAction,
    ConfigAction,
    ReloadConfigAction,
    SelfUpdateAction,
    check_for_update,
    coerce_version,
    get_binary_destination_path,
    get_latest_release,
    get_local_binary_path,
    print_version,
)


def _github_response(mocker: MockerFixture, tag_name: str | None):
    response = mocker.Mock()
    response.json.return_value = {"tag_name": tag_name}
    return mocker.patch("requests.get", return_value=response)


class TestGetLatestRelease:
    def test_leading_v_is_stripped_from_the_version(self, mocker: MockerFixture):
        _github_response(mocker, "v2.1.0")

        assert get_latest_release("some/repository") == ("2.1.0", "v2.1.0")

    def test_tag_without_leading_v_is_used_as_is(self, mocker: MockerFixture):
        _github_response(mocker, "2.1.0")

        assert get_latest_release("some/repository") == ("2.1.0", "2.1.0")

    def test_release_without_tag(self, mocker: MockerFixture):
        _github_response(mocker, None)

        assert get_latest_release("some/repository") == (None, None)

    def test_http_error_is_swallowed(self, mocker: MockerFixture):
        response = mocker.Mock()
        response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
        mocker.patch("requests.get", return_value=response)

        assert get_latest_release("some/repository") == (None, None)


class TestCoerceVersion:
    def test_missing_components_default_to_zero(self):
        version, rest = coerce_version("v2.1")

        assert (version.major, version.minor, version.patch) == (2, 1, 0)
        assert rest == ""

    def test_trailing_content_is_returned(self):
        version, rest = coerce_version("2.1.0-beta")

        assert (version.major, version.minor, version.patch) == (2, 1, 0)
        assert rest == "-beta"

    def test_string_without_version(self):
        assert coerce_version("not-a-version") == (None, "not-a-version")


class TestPrintVersion:
    def test_silent_prints_the_version_only(self, capsys: CaptureFixture, mocker: MockerFixture):
        get_latest = mocker.patch("ddb.feature.core.actions.get_latest_release")

        print_version("some/repository", silent=True)

        assert capsys.readouterr().out.strip() == __version__
        get_latest.assert_not_called()

    def test_update_is_advertised(self, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.get_latest_release", return_value=("99.0.0", "v99.0.0"))

        print_version("some/repository")

        out = capsys.readouterr().out
        assert "A new version is available: 99.0.0" in out
        assert "https://github.com/some/repository/releases/tag/v99.0.0" in out

    def test_up_to_date_version_is_not_advertised(self, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.get_latest_release", return_value=(None, None))

        print_version("some/repository")

        assert "A new version is available" not in capsys.readouterr().out


class TestCheckForUpdate:
    def test_details_are_displayed(self, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.get_latest_release", return_value=("99.0.0", "v99.0.0"))

        assert check_for_update("some/repository", output=True, details=True) == ("99.0.0", "v99.0.0")

        out = capsys.readouterr().out
        assert "A new version is available: 99.0.0" in out
        assert "https://github.com/some/repository/releases/tag/v99.0.0" in out

    def test_header_only_is_displayed_without_details(self, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.get_latest_release", return_value=("99.0.0", "v99.0.0"))

        check_for_update("some/repository", output=True)

        out = capsys.readouterr().out
        assert "A new version is available: 99.0.0" in out
        assert "releases/tag" not in out

    def test_nothing_is_displayed_when_up_to_date(self, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.get_latest_release", return_value=("0.0.1", "v0.0.1"))

        assert check_for_update("some/repository", output=True) == (None, None)
        assert capsys.readouterr().out == ""


class TestGetLocalBinaryPath:
    def test_executable_is_preferred(self, monkeypatch, tmp_path):
        binary = tmp_path / "ddb"
        binary.touch()
        monkeypatch.setattr(sys, "executable", str(binary))

        assert get_local_binary_path() == str(binary)

    def test_absolute_argv0_is_used(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(sys, "argv", [str(tmp_path / "ddb")])

        assert get_local_binary_path() == str(tmp_path / "ddb")

    def test_bare_argv0_is_resolved_against_the_home_bin_directory(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(sys, "argv", ["ddb"])
        monkeypatch.setattr(config, "paths", config.paths._replace(home=str(tmp_path)))

        assert get_local_binary_path() == str(tmp_path / "bin" / "ddb")

    def test_relative_argv0_is_resolved_against_the_current_working_directory(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(sys, "argv", [str(Path("bin") / "ddb")])
        monkeypatch.setattr(config, "cwd", str(tmp_path))

        assert get_local_binary_path() == str(tmp_path / "bin" / "ddb")

    def test_unresolvable_binary_path_is_rejected(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(sys, "argv", [str(Path("bin") / "ddb")])
        monkeypatch.setattr(config, "cwd", None)

        with pytest.raises(ValueError, match=re.escape("Can't find local binary path to update.")):
            get_local_binary_path()


class TestGetBinaryDestinationPath:
    def test_platform_qualifier_is_dropped(self):
        assert get_binary_destination_path("/usr/local/bin/ddb-linux") == "/usr/local/bin/ddb"

    def test_development_entry_point_is_not_overwritten(self, tmp_path):
        source = tmp_path / "ddb.py"
        source.write_text("#!/usr/bin/env python\nprint('ddb')\n")

        assert get_binary_destination_path(str(source)) == str(tmp_path / "ddb.bin")

    def test_other_python_files_are_kept(self, tmp_path):
        source = tmp_path / "ddb.py"
        source.write_text("print('ddb')\n")

        assert get_binary_destination_path(str(source)) == str(source)


class TestConfigActionOutput:
    def test_scalar_configuration_is_printed_as_is(self, capsys: CaptureFixture):
        config.args.files = False

        ConfigAction._print_config_yaml("some-value", None)

        assert capsys.readouterr().out.strip() == "some-value"

    def test_empty_configuration_prints_nothing(self, capsys: CaptureFixture):
        config.args.files = False

        ConfigAction._print_config_yaml(None, None)

        assert capsys.readouterr().out == ""

    def test_variables_are_printed_per_file(self, capsys: CaptureFixture):
        config.args.files = True
        configuration_files = {"ddb.yml": {"app": {"value": "default"}}, "ddb.local.yml": {"app": {"value": "local"}}}

        ConfigAction._print_config_variables(None, configuration_files)

        assert capsys.readouterr().out == ("# ddb.yml\napp.value: default\n\n# ddb.local.yml\napp.value: local\n")

    def test_missing_value_is_rejected(self):
        with pytest.raises(ValueError, match=re.escape("app.value not found in configuration.")):
            ConfigAction._print_config_value(None, "app.value")

    def test_unknown_property_is_rejected(self):
        with pytest.raises(ValueError, match=re.escape("app.missing not found in configuration.")):
            ConfigAction._print_config_value({"app": {"value": "default"}}, "app.missing")

    def test_whole_configuration_is_printed_without_property(self, capsys: CaptureFixture):
        ConfigAction._print_config_value({"app": "value"}, None)

        assert capsys.readouterr().out.strip() == "{'app': 'value'}"


class TestPruneDefaultConfiguration:
    def test_keys_defined_in_a_file_are_removed_from_the_defaults(self):
        default_configuration = {"app.value": "default", "app.other": "default", "core.domain.ext": "test"}

        ConfigAction._prune_default_configuration(default_configuration, {"app.value": "app.value"})

        assert default_configuration == {"app.other": "default", "core.domain.ext": "test"}

    def test_emptied_parents_are_removed_too(self):
        default_configuration = {"app.value": "default", "app": {}}

        ConfigAction._prune_default_configuration(default_configuration, {"app.value": "app.value"})

        assert default_configuration == {}

    def test_parents_still_holding_values_are_kept(self):
        default_configuration = {"app.value": "default", "app": {"other": "default"}}

        ConfigAction._prune_default_configuration(default_configuration, {"app.value": "app.value"})

        assert default_configuration == {"app": {"other": "default"}}


class TestReloadConfigAction:
    def test_reload_failure_is_logged(self, mocker: MockerFixture, caplog):
        mocker.patch.object(context, "watching", new=True)
        mocker.patch.object(config, "read", return_value=({}, {}))
        mocker.patch.object(config, "load_from_data", side_effect=ValueError("broken configuration"))

        ReloadConfigAction.execute("ddb.yml")

        assert "Configuration has fail to reload: broken configuration" in caplog.text


class TestCheckForUpdateAction:
    @pytest.fixture
    def action(self):
        action = CheckForUpdateAction()
        action.initialize()
        # The cache is global and outlives the test session.
        caches.get("core.check_for_update.version").clear()
        return action

    @staticmethod
    def _command(mocker: MockerFixture, *, avoid_stdout: bool = False):
        return mocker.Mock(avoid_stdout=avoid_stdout)

    def test_update_is_checked_once_a_day(self, action, mocker: MockerFixture):
        config.data["core.check_updates"] = True
        check = mocker.patch("ddb.feature.core.actions.check_for_update", return_value=(None, None))

        action.execute(self._command(mocker))
        action.execute(self._command(mocker))

        check.assert_called_once()
        assert caches.get("core.check_for_update.version").get("last_check") is not None

    def test_nothing_is_checked_when_updates_are_disabled(self, action, mocker: MockerFixture):
        config.data["core.check_updates"] = False
        check = mocker.patch("ddb.feature.core.actions.check_for_update")

        action.execute(self._command(mocker))

        check.assert_not_called()

    def test_nothing_is_checked_for_commands_avoiding_stdout(self, action, mocker: MockerFixture):
        config.data["core.check_updates"] = True
        check = mocker.patch("ddb.feature.core.actions.check_for_update")

        action.execute(self._command(mocker, avoid_stdout=True))

        check.assert_not_called()


class TestSelfUpdateBinary:
    def test_read_only_binary_is_rejected(self, mocker: MockerFixture, tmp_path):
        binary = tmp_path / "ddb"
        binary.touch()
        mocker.patch("ddb.feature.core.actions.get_local_binary_path", return_value=str(binary))
        mocker.patch("os.access", return_value=False)

        with pytest.raises(PermissionError, match=re.escape("You don't have permission to write on ddb binary file.")):
            SelfUpdateAction.self_update_binary("some/repository", "v99.0.0")

    def test_binary_path_that_is_not_a_file_is_rejected(self, mocker: MockerFixture, tmp_path):
        mocker.patch("ddb.feature.core.actions.get_local_binary_path", return_value=str(tmp_path))

        with pytest.raises(ValueError, match=re.escape("Local binary path is not a file.")):
            SelfUpdateAction.self_update_binary("some/repository", "v99.0.0")

    def test_platform_without_release_asset_is_reported(self, mocker: MockerFixture, tmp_path, capsys: CaptureFixture):
        binary = tmp_path / "ddb"
        binary.touch()
        mocker.patch("ddb.feature.core.actions.get_local_binary_path", return_value=str(binary))
        config.data["core.release_asset_name"] = None

        SelfUpdateAction.self_update_binary("some/repository", "v99.0.0")

        assert "platform that doesn't support binary package mode" in capsys.readouterr().out


class TestSelfUpdateAction:
    def test_package_mode_is_reported(self, mocker: MockerFixture, capsys: CaptureFixture):
        mocker.patch("ddb.feature.core.actions.is_binary", return_value=False)
        config.data["core.github_repository"] = "some/repository"

        SelfUpdateAction().execute()

        out = capsys.readouterr().out
        assert "doesn't support self-update" in out
        assert "https://github.com/some/repository/releases" in out

    def test_up_to_date_binary_is_not_updated(self, mocker: MockerFixture, capsys: CaptureFixture):
        mocker.patch("ddb.feature.core.actions.is_binary", return_value=True)
        mocker.patch("ddb.feature.core.actions.check_for_update", return_value=(None, None))
        self_update_binary = mocker.patch.object(SelfUpdateAction, "self_update_binary")
        config.data["core.github_repository"] = "some/repository"

        SelfUpdateAction().execute()

        assert "ddb is already up to date." in capsys.readouterr().out
        self_update_binary.assert_not_called()

    def test_up_to_date_binary_is_updated_when_forced(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.is_binary", return_value=True)
        mocker.patch("ddb.feature.core.actions.check_for_update", return_value=(None, None))
        mocker.patch("ddb.feature.core.actions.get_current_version", return_value="1.2.3")
        self_update_binary = mocker.patch.object(SelfUpdateAction, "self_update_binary")
        config.data["core.github_repository"] = "some/repository"
        config.args.force = True

        SelfUpdateAction().execute()

        self_update_binary.assert_called_once_with("some/repository", "v1.2.3")

    def test_outdated_binary_is_updated(self, mocker: MockerFixture):
        mocker.patch("ddb.feature.core.actions.is_binary", return_value=True)
        mocker.patch("ddb.feature.core.actions.check_for_update", return_value=("99.0.0", "v99.0.0"))
        self_update_binary = mocker.patch.object(SelfUpdateAction, "self_update_binary")
        config.data["core.github_repository"] = "some/repository"

        SelfUpdateAction().execute()

        self_update_binary.assert_called_once_with("some/repository", "v99.0.0")
