import os
import shutil
import threading
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

import pytest
from ddb.__main__ import main, wait_watch_started, stop_watch
from tests.utilstest import expect_gitignore, setup_cfssl
from waiting import wait


def init_test_watch(watch: bool, command: Iterable[str]):
    thread = None

    full_command = ["--watch"] if watch else []
    full_command.extend(command)

    main_runner = lambda: main(full_command)

    if watch:
        thread = threading.Thread(name="watch",
                                  target=main_runner)
        thread.start()
        wait_watch_started(30)
        if os.environ.get("TRAVIS") == "true":
            # On TravisCI, it seems there is some race condition that may cause tests to fail without this.
            time.sleep(1)
    else:
        main_runner()

    return thread, main_runner


class TestWatch:
    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_change(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            with open("test.txt.jinja", "w") as template_file:
                template_file.write("This is {{core.project.name}} project. (modified)")

            if not watch:
                main_runner()

            wait(lambda: os.path.exists("test.txt") and
                         Path("test.txt").read_text() == "This is watch1 project. (modified)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists(".gitignore") and expect_gitignore(".gitignore", "/test.txt"),
                 timeout_seconds=5)
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_created(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            with open("test.created.txt.jinja", "w") as template_file:
                template_file.write("This is {{core.project.name}} project. (created)")

            if not watch:
                main_runner()

            wait(lambda: os.path.exists("test.created.txt") and
                         Path("test.created.txt").read_text() == "This is watch1 project. (created)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists(".gitignore") and
                         expect_gitignore(".gitignore", "/test.txt", "/test.created.txt"),
                 timeout_seconds=5)
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_delete(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            os.remove("test.txt.jinja")

            if not watch:
                main_runner()

            wait(lambda: not os.path.exists("test.txt"), timeout_seconds=5)
            wait(lambda: not expect_gitignore(".gitignore", "/text.txt"), timeout_seconds=5)
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_move(self, project_loader, watch):
        project_loader("watch1")

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            os.rename("test.txt.jinja", "test2.txt.jinja")

            if not watch:
                main_runner()

            wait(lambda: not os.path.exists("test.txt") and os.path.exists("test2.txt") and "This is watch1 project.",
                 timeout_seconds=5)

            wait(lambda: os.path.exists(".gitignore") and expect_gitignore(".gitignore", "/test2.txt"),
                 timeout_seconds=5)
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()


def copy_from_files(f):
    with NamedTemporaryFile('w', delete=False) as tmp:
        with open(os.path.join("..", "files", f)) as source:
            shutil.copyfileobj(source, tmp)

    os.rename(tmp.name, f)


class TestWatchFixuid:
    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_fixuid_order_1(self, project_loader, watch):
        project_loader("watch-fixuid")

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            os.makedirs(os.path.join(".docker", "db"), exist_ok=True)

            copy_from_files(os.path.join(".docker", "db", "Dockerfile.jinja"))
            assert os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))

            copy_from_files(os.path.join(".docker", "db", "fixuid.yml"))
            assert os.path.exists(os.path.join(".docker", "db", "fixuid.yml"))

            copy_from_files("docker-compose.yml.jsonnet")
            assert os.path.exists("docker-compose.yml.jsonnet")

            if not watch:
                main_runner()

            wait(lambda: os.path.exists(os.path.join(".docker", "db", "Dockerfile")),
                 timeout_seconds=30)

            wait(lambda: os.path.exists("docker-compose.yml"),
                 timeout_seconds=30)

            def check_dockerfile():
                with open(os.path.join("..", "expected", "Dockerfile"), "r") as file:
                    expected_dockerfile = file.read()

                with open(os.path.join(".docker", "db", "Dockerfile"), "r") as file:
                    actual_dockerfile = file.read()

                return expected_dockerfile == actual_dockerfile

            wait(check_dockerfile, timeout_seconds=30)

        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()

    @pytest.mark.parametrize("parameters", [
        [True, ["docker-compose.yml.jsonnet",
                os.path.join(".docker", "db", "Dockerfile.jinja"),
                os.path.join(".docker", "db", "fixuid.yml")]],
        [False, ["docker-compose.yml.jsonnet",
                 os.path.join(".docker", "db", "Dockerfile.jinja"),
                 os.path.join(".docker", "db", "fixuid.yml")]],
        [True, [os.path.join(".docker", "db", "Dockerfile.jinja"),
                os.path.join(".docker", "db", "fixuid.yml"),
                "docker-compose.yml.jsonnet", ]],
        [False, [os.path.join(".docker", "db", "Dockerfile.jinja"),
                 os.path.join(".docker", "db", "fixuid.yml"),
                 "docker-compose.yml.jsonnet"]],
        [True, [os.path.join(".docker", "db", "fixuid.yml"),
                "docker-compose.yml.jsonnet",
                os.path.join(".docker", "db", "Dockerfile.jinja")]],
        [False, [os.path.join(".docker", "db", "fixuid.yml"),
                 "docker-compose.yml.jsonnet",
                 os.path.join(".docker", "db", "Dockerfile.jinja")]],
    ])
    def test_watch_fixuid_various_order(self, project_loader, parameters):
        watch, files = parameters
        project_loader("watch-fixuid")

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            os.makedirs(os.path.join(".docker", "db"), exist_ok=True)

            for f in files:
                copy_from_files(f)
                time.sleep(0.5)

            if not watch:
                main_runner()

            wait(lambda: os.path.exists(os.path.join(".docker", "db", "Dockerfile")),
                 timeout_seconds=30)

            wait(lambda: os.path.exists("docker-compose.yml"),
                 timeout_seconds=30)

            wait(lambda: os.path.exists(os.path.join(".docker", "db", "fixuid.tar.gz")),
                 timeout_seconds=30)

            def _check_dockerfile():
                with open(os.path.join("..", "expected", "Dockerfile"), "r") as file:
                    expected_dockerfile = file.read()

                with open(os.path.join(".docker", "db", "Dockerfile"), "r") as file:
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

        thread, main_runner = init_test_watch(True, ["configure"])

        try:
            wait(lambda: os.path.exists("test.txt") and Path("test.txt").read_text() == "app.value: foo",
                 timeout_seconds=60)

            with open("ddb.yml", "r") as f:
                ddb_yml_content = f.read()

            ddb_yml_content = ddb_yml_content.replace("foo", "bar")
            with open("ddb.yml", "w") as f:
                f.write(ddb_yml_content)

            time.sleep(5)

            wait(lambda: os.path.exists("test.txt") and Path("test.txt").read_text() == "app.value: bar",
                 timeout_seconds=60)
        finally:
            stop_watch()

        if thread:
            thread.join()


class TestWatchCerts:
    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    @pytest.mark.docker
    def test_watch_certificates_when_virtualhost_is_added(self, watch, project_loader, module_scoped_container_getter):
        project_loader("watch-certs")

        setup_cfssl(module_scoped_container_getter)

        thread, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert not os.path.exists(os.path.join(".certs", "watch-certs.test.key"))
            assert not os.path.exists(os.path.join(".certs", "watch-certs.test.crt"))

            copy_from_files("docker-compose.yml.jsonnet")

            if not watch:
                main_runner()

            wait(lambda: os.path.exists("docker-compose.yml"), timeout_seconds=5)
            wait(lambda: not os.path.exists(os.path.join(".certs", "watch-certs.test.key")), timeout_seconds=5)
            wait(lambda: not os.path.exists(os.path.join(".certs", "watch-certs.test.crt")), timeout_seconds=5)

            with open("docker-compose.yml.jsonnet", "r") as f:
                ddb_yml_content = f.read()

            ddb_yml_content = ddb_yml_content.replace('ddb.Image("httpd")',
                                                      'ddb.Image("httpd") + ddb.VirtualHost("80", "watch-certs.test", "httpd")')
            with open("docker-compose.yml.jsonnet", "w") as f:
                f.write(ddb_yml_content)

            if not watch:
                main_runner()

            wait(lambda: os.path.exists(os.path.join(".certs", "watch-certs.test.key")), timeout_seconds=5)
            wait(lambda: os.path.exists(os.path.join(".certs", "watch-certs.test.crt")), timeout_seconds=5)
            wait(lambda: os.path.exists(os.path.join("..", "home", "certs", "watch-certs.test.key")), timeout_seconds=5)
            wait(lambda: os.path.exists(os.path.join("..", "home", "certs", "watch-certs.test.crt")), timeout_seconds=5)
            wait(lambda: os.path.exists(os.path.join("..", "home", "traefik", "config", "watch-certs.test.ssl.toml")),
                 timeout_seconds=5)

            ssl_configuration = Path(
                os.path.join("..", "home", "traefik", "config", "watch-certs.test.ssl.toml")).read_text()

            assert ssl_configuration == '''# This configuration file has been automatically generated by ddb
[[tls.certificates]]
  certFile = "/certs/watch-certs.test.crt"
  keyFile = "/certs/watch-certs.test.key"
'''

            ddb_yml_content = ddb_yml_content.replace(
                'ddb.Image("httpd") + ddb.VirtualHost("80", "watch-certs.test", "httpd")',
                'ddb.Image("httpd")')

            with open("docker-compose.yml.jsonnet", "w") as f:
                f.write(ddb_yml_content)

            if not watch:
                main_runner()

            wait(lambda: not os.path.exists(os.path.join(".certs", "watch-certs.test.key")), timeout_seconds=5)
            wait(lambda: not os.path.exists(os.path.join(".certs", "watch-certs.test.crt")), timeout_seconds=5)
            wait(lambda: not os.path.exists(os.path.join("..", "home", "certs", "watch-certs.test.key")),
                 timeout_seconds=5)
            wait(lambda: not os.path.exists(os.path.join("..", "home", "certs", "watch-certs.test.crt")),
                 timeout_seconds=5)
            wait(lambda: not os.path.exists(
                os.path.join("..", "home", "traefik", "config", "watch-certs.test.ssl.toml")),
                 timeout_seconds=5)
        finally:
            if watch:
                stop_watch()

        if thread:
            thread.join()
