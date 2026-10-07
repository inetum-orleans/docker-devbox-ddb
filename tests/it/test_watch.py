import shutil
import threading
import time
from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from waiting import wait

from ddb.__main__ import main, stop_watch, wait_watch_started
from tests.utilstest import expect_gitignore, setup_cfssl

# The watchers report changes asynchronously, and macOS coalesces them behind FSEvents.
WATCH_TIMEOUT = 20

# wait_watch_started returns as soon as the observers are started, but the watches they
# install, and the events macOS has already coalesced, need a moment to settle.
WATCH_SETTLE_DELAY = 2


def init_test_watch(command: Iterable[str], *, watch: bool):
    thread = None

    full_command = ["--watch"] if watch else []
    full_command.extend(command)

    def main_runner():
        return main(full_command)

    if watch:
        thread = threading.Thread(name="watch", target=main_runner)
        thread.start()
        wait_watch_started(30)
        time.sleep(WATCH_SETTLE_DELAY)
    else:
        main_runner()

    return thread, main_runner


class TestWatch:
    @pytest.mark.parametrize("watch", [True, False])
    def test_watch_file_change(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            assert Path("test.txt").exists()

            with Path("test.txt.jinja").open("w") as template_file:
                template_file.write("This is {{core.project.name}} project. (modified)")

            if not watch:
                main_runner()

            wait(
                lambda: (
                    Path("test.txt").exists() and Path("test.txt").read_text() == "This is watch1 project. (modified)"
                ),
                timeout_seconds=WATCH_TIMEOUT,
            )

            wait(
                lambda: Path(".gitignore").exists() and expect_gitignore(".gitignore", "/test.txt"),
                timeout_seconds=WATCH_TIMEOUT,
            )
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [True, False])
    def test_watch_file_created(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            assert Path("test.txt").exists()

            with Path("test.created.txt.jinja").open("w") as template_file:
                template_file.write("This is {{core.project.name}} project. (created)")

            if not watch:
                main_runner()

            wait(
                lambda: (
                    Path("test.created.txt").exists()
                    and Path("test.created.txt").read_text() == "This is watch1 project. (created)"
                ),
                timeout_seconds=WATCH_TIMEOUT,
            )

            wait(
                lambda: (
                    Path(".gitignore").exists() and expect_gitignore(".gitignore", "/test.txt", "/test.created.txt")
                ),
                timeout_seconds=WATCH_TIMEOUT,
            )
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [True, False])
    def test_watch_file_delete(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            assert Path("test.txt").exists()

            Path("test.txt.jinja").unlink()

            if not watch:
                main_runner()

            wait(lambda: not Path("test.txt").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(lambda: not expect_gitignore(".gitignore", "/text.txt"), timeout_seconds=WATCH_TIMEOUT)
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [True, False])
    def test_watch_file_move(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            assert Path("test.txt").exists()

            Path("test.txt.jinja").rename("test2.txt.jinja")

            if not watch:
                main_runner()

            wait(
                lambda: not Path("test.txt").exists() and Path("test2.txt").exists() and "This is watch1 project.",
                timeout_seconds=WATCH_TIMEOUT,
            )

            wait(
                lambda: Path(".gitignore").exists() and expect_gitignore(".gitignore", "/test2.txt"),
                timeout_seconds=WATCH_TIMEOUT,
            )
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()


def copy_from_files(f):
    with NamedTemporaryFile("w", delete=False) as tmp, (Path("..") / "files" / f).open() as source:
        shutil.copyfileobj(source, tmp)

    Path(tmp.name).rename(f)


def rewrite_watched(f, content):
    """
    Replace a watched file in a single step.

    Rewriting it in place opens a window where the watcher reads the truncated file, and a template that fails to
    render aborts the whole watch run.
    """
    with NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write(content)

    Path(tmp.name).replace(f)


class TestWatchFixuid:
    @pytest.mark.parametrize("watch", [True, False])
    def test_watch_fixuid_order_1(self, project_loader, watch):
        project_loader("watch-fixuid")

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            (Path(".docker") / "db").mkdir(parents=True, exist_ok=True)

            copy_from_files(str(Path(".docker") / "db" / "Dockerfile.jinja"))
            assert (Path(".docker") / "db" / "Dockerfile.jinja").exists()

            copy_from_files(str(Path(".docker") / "db" / "fixuid.yml"))
            assert (Path(".docker") / "db" / "fixuid.yml").exists()

            copy_from_files("docker-compose.yml.jsonnet")
            assert Path("docker-compose.yml.jsonnet").exists()

            if not watch:
                main_runner()

            wait(lambda: (Path(".docker") / "db" / "Dockerfile").exists(), timeout_seconds=30)

            wait(lambda: Path("docker-compose.yml").exists(), timeout_seconds=30)

            def check_dockerfile():
                with (Path("..") / "expected" / "Dockerfile").open() as file:
                    expected_dockerfile = file.read()

                with (Path(".docker") / "db" / "Dockerfile").open() as file:
                    actual_dockerfile = file.read()

                return expected_dockerfile == actual_dockerfile

            wait(check_dockerfile, timeout_seconds=30)

        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize(
        "parameters",
        [
            [
                True,
                [
                    "docker-compose.yml.jsonnet",
                    str(Path(".docker") / "db" / "Dockerfile.jinja"),
                    str(Path(".docker") / "db" / "fixuid.yml"),
                ],
            ],
            [
                False,
                [
                    "docker-compose.yml.jsonnet",
                    str(Path(".docker") / "db" / "Dockerfile.jinja"),
                    str(Path(".docker") / "db" / "fixuid.yml"),
                ],
            ],
            [
                True,
                [
                    str(Path(".docker") / "db" / "Dockerfile.jinja"),
                    str(Path(".docker") / "db" / "fixuid.yml"),
                    "docker-compose.yml.jsonnet",
                ],
            ],
            [
                False,
                [
                    str(Path(".docker") / "db" / "Dockerfile.jinja"),
                    str(Path(".docker") / "db" / "fixuid.yml"),
                    "docker-compose.yml.jsonnet",
                ],
            ],
            [
                True,
                [
                    str(Path(".docker") / "db" / "fixuid.yml"),
                    "docker-compose.yml.jsonnet",
                    str(Path(".docker") / "db" / "Dockerfile.jinja"),
                ],
            ],
            [
                False,
                [
                    str(Path(".docker") / "db" / "fixuid.yml"),
                    "docker-compose.yml.jsonnet",
                    str(Path(".docker") / "db" / "Dockerfile.jinja"),
                ],
            ],
        ],
    )
    def test_watch_fixuid_various_order(self, project_loader, parameters):
        watch, files = parameters
        project_loader("watch-fixuid")

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            (Path(".docker") / "db").mkdir(parents=True, exist_ok=True)

            for f in files:
                copy_from_files(f)
                time.sleep(0.5)

            if not watch:
                main_runner()

            wait(lambda: (Path(".docker") / "db" / "Dockerfile").exists(), timeout_seconds=30)

            wait(lambda: Path("docker-compose.yml").exists(), timeout_seconds=30)

            wait(lambda: (Path(".docker") / "db" / "fixuid.tar.gz").exists(), timeout_seconds=30)

            def _check_dockerfile():
                with (Path("..") / "expected" / "Dockerfile").open() as file:
                    expected_dockerfile = file.read()

                with (Path(".docker") / "db" / "Dockerfile").open() as file:
                    actual_dockerfile = file.read()

                return expected_dockerfile == actual_dockerfile

            wait(_check_dockerfile, timeout_seconds=30)

        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()


class TestWatchConfig:
    def test_watch_config_change(self, project_loader):
        project_loader("watch-config")

        thread, _main_runner = init_test_watch(["configure"], watch=True)

        try:
            wait(
                lambda: Path("test.txt").exists() and Path("test.txt").read_text() == "app.value: foo",
                timeout_seconds=60,
            )

            with Path("ddb.yml").open() as f:
                ddb_yml_content = f.read()

            ddb_yml_content = ddb_yml_content.replace("foo", "bar")
            rewrite_watched("ddb.yml", ddb_yml_content)

            time.sleep(5)

            wait(
                lambda: Path("test.txt").exists() and Path("test.txt").read_text() == "app.value: bar",
                timeout_seconds=60,
            )
        finally:
            stop_watch()

        if thread:
            thread.join()


class TestWatchCerts:
    @pytest.mark.parametrize("watch", [True, False])
    @pytest.mark.docker
    def test_watch_certificates_when_virtualhost_is_added(self, watch, project_loader, module_scoped_container_getter):
        project_loader("watch-certs")

        setup_cfssl(module_scoped_container_getter)

        thread, main_runner = init_test_watch(["configure"], watch=watch)

        try:
            assert not (Path(".certs") / "watch-certs.test.key").exists()
            assert not (Path(".certs") / "watch-certs.test.crt").exists()

            copy_from_files("docker-compose.yml.jsonnet")

            if not watch:
                main_runner()

            wait(lambda: Path("docker-compose.yml").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(lambda: not (Path(".certs") / "watch-certs.test.key").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(lambda: not (Path(".certs") / "watch-certs.test.crt").exists(), timeout_seconds=WATCH_TIMEOUT)

            with Path("docker-compose.yml.jsonnet").open() as f:
                ddb_yml_content = f.read()

            ddb_yml_content = ddb_yml_content.replace(
                'ddb.Image("httpd")', 'ddb.Image("httpd") + ddb.VirtualHost("80", "watch-certs.test", "httpd")'
            )
            rewrite_watched("docker-compose.yml.jsonnet", ddb_yml_content)

            if not watch:
                main_runner()

            wait(lambda: (Path(".certs") / "watch-certs.test.key").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(lambda: (Path(".certs") / "watch-certs.test.crt").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(
                lambda: (Path("..") / "home" / "certs" / "watch-certs.test.key").exists(), timeout_seconds=WATCH_TIMEOUT
            )
            wait(
                lambda: (Path("..") / "home" / "certs" / "watch-certs.test.crt").exists(), timeout_seconds=WATCH_TIMEOUT
            )
            wait(
                lambda: (Path("..") / "home" / "traefik" / "config" / "watch-certs.test.ssl.toml").exists(),
                timeout_seconds=WATCH_TIMEOUT,
            )

            ssl_configuration = Path(
                str(Path("..") / "home" / "traefik" / "config" / "watch-certs.test.ssl.toml")
            ).read_text()

            assert (
                ssl_configuration
                == """# This configuration file has been automatically generated by ddb
[[tls.certificates]]
  certFile = "/certs/watch-certs.test.crt"
  keyFile = "/certs/watch-certs.test.key"
"""
            )

            ddb_yml_content = ddb_yml_content.replace(
                'ddb.Image("httpd") + ddb.VirtualHost("80", "watch-certs.test", "httpd")', 'ddb.Image("httpd")'
            )

            rewrite_watched("docker-compose.yml.jsonnet", ddb_yml_content)

            if not watch:
                main_runner()

            wait(lambda: not (Path(".certs") / "watch-certs.test.key").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(lambda: not (Path(".certs") / "watch-certs.test.crt").exists(), timeout_seconds=WATCH_TIMEOUT)
            wait(
                lambda: not (Path("..") / "home" / "certs" / "watch-certs.test.key").exists(),
                timeout_seconds=WATCH_TIMEOUT,
            )
            wait(
                lambda: not (Path("..") / "home" / "certs" / "watch-certs.test.crt").exists(),
                timeout_seconds=WATCH_TIMEOUT,
            )
            wait(
                lambda: not (Path("..") / "home" / "traefik" / "config" / "watch-certs.test.ssl.toml").exists(),
                timeout_seconds=WATCH_TIMEOUT,
            )
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()
