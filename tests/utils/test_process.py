import subprocess

from pytest_mock import MockerFixture

from ddb.config import config
from ddb.utils.process import effective_command, run


def _completed(stdout: bytes) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout)


class TestEffectiveCommand:
    def test_executable_and_args_are_kept_as_is(self):
        assert effective_command("git", "rev-parse", "HEAD") == ["git", "rev-parse", "HEAD"]

    def test_executable_alone_is_split_into_args(self):
        assert effective_command("git rev-parse HEAD") == ["git", "rev-parse", "HEAD"]

    def test_executable_alone_is_split_honoring_quotes(self):
        assert effective_command('git commit -m "some message"') == ["git", "commit", "-m", "some message"]

    def test_configured_bin_replaces_the_executable(self):
        config.data["core.process.git.bin"] = "/usr/local/bin/git"

        assert effective_command("git", "status") == ["/usr/local/bin/git", "status"]

    def test_configured_list_args_are_prepended_and_appended(self):
        config.data["core.process.git.prepend"] = ["-c", "core.autocrlf=false"]
        config.data["core.process.git.append"] = ["--quiet"]

        assert effective_command("git", "status") == ["git", "-c", "core.autocrlf=false", "status", "--quiet"]

    def test_configured_string_args_are_split(self):
        config.data["core.process.git.prepend"] = '-c "core.autocrlf=false"'
        config.data["core.process.git.append"] = "--quiet"

        assert effective_command("git", "status") == ["git", "-c", "core.autocrlf=false", "status", "--quiet"]

    def test_exe_extension_is_added_on_windows(self, mocker: MockerFixture):
        mocker.patch("ddb.utils.process.os.name", "nt")

        assert effective_command("git", "status") == ["git.exe", "status"]

    def test_exe_extension_is_not_duplicated_on_windows(self, mocker: MockerFixture):
        mocker.patch("ddb.utils.process.os.name", "nt")
        config.data["core.process.git.bin"] = "git.exe"

        assert effective_command("git", "status") == ["git.exe", "status"]


class TestRun:
    def test_stdout_is_returned(self, mocker: MockerFixture):
        subprocess_run = mocker.patch("subprocess.run", return_value=_completed(b"some output"))

        assert run("git", "status") == b"some output"
        subprocess_run.assert_called_once_with(["git", "status"], check=True, capture_output=True)

    def test_windows_ansi_reset_suffix_is_dropped(self, mocker: MockerFixture):
        mocker.patch("ddb.utils.process.os.name", "nt")
        mocker.patch("subprocess.run", return_value=_completed(b"some output\x1b[0m\r\n"))

        assert run("git.exe", "status") == b"some output"

    def test_windows_stdout_is_kept_when_there_is_no_ansi_reset_suffix(self, mocker: MockerFixture):
        mocker.patch("ddb.utils.process.os.name", "nt")
        mocker.patch("subprocess.run", return_value=_completed(b"some output"))

        assert run("git.exe", "status") == b"some output"
