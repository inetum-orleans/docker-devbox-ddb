import os
import shutil
import threading
import time
from pathlib import Path
from typing import Iterable

import pytest
from waiting import wait

from ddb.__main__ import main
from tests.utilstest import expect_gitignore


def init_test_watch(watch: bool, command: Iterable[str]):
    thread = None
    watch_stop_event = threading.Event()
    watch_started_event = threading.Event()

    full_command = ["--watch"] if watch else []
    full_command.extend(command)

    main_runner = lambda: main(full_command,
                               watch_started_event,
                               watch_stop_event)

    if watch:
        thread = threading.Thread(name="watch",
                                  target=main_runner)
        thread.start()
        watch_started_event.wait(30)
        if os.environ.get("TRAVIS") == "true":
            # On TravisCI, it seems there is some race condition that may cause tests to fail without this.
            time.sleep(1)
    else:
        main_runner()

    return thread, watch_stop_event, watch_started_event, main_runner


class TestWatch:
    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_change(self, project_loader, watch):
        project_loader("watch1")

        thread, watch_stop_event, watch_started_event, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            with open("test.txt.jinja", "w") as template_file:
                template_file.write("This is {{core.project.name}} project. (modified)")

            if not watch:
                main_runner()

            wait(lambda: os.path.exists("test.txt") and
                         Path("test.txt").read_text() == "This is watch1 project. (modified)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists(".gitignore") and expect_gitignore(".gitignore", "test.txt"),
                 timeout_seconds=5)
        finally:
            if watch:
                watch_stop_event.set()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_created(self, project_loader, watch):
        project_loader("watch1")

        thread, watch_stop_event, watch_started_event, main_runner = init_test_watch(watch, ["configure"])

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
                         expect_gitignore(".gitignore", "test.txt", "test.created.txt"),
                 timeout_seconds=5)
        finally:
            if watch:
                watch_stop_event.set()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_delete(self, project_loader, watch):
        project_loader("watch1")

        thread, watch_stop_event, watch_started_event, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            os.remove("test.txt.jinja")

            if not watch:
                main_runner()

            wait(lambda: not os.path.exists("test.txt"), timeout_seconds=5)
            wait(lambda: not expect_gitignore(".gitignore", "text.txt"), timeout_seconds=5)
        finally:
            if watch:
                watch_stop_event.set()

        if thread:
            thread.join()

    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_file_move(self, project_loader, watch):
        project_loader("watch1")

        thread, watch_stop_event, watch_started_event, main_runner = init_test_watch(watch, ["configure"])

        try:
            assert os.path.exists("test.txt")

            os.rename("test.txt.jinja", "test2.txt.jinja")

            if not watch:
                main_runner()

            wait(lambda: not os.path.exists("test.txt") and os.path.exists("test2.txt") and "This is watch1 project.",
                 timeout_seconds=5)

            wait(lambda: os.path.exists(".gitignore") and expect_gitignore(".gitignore", "test2.txt"),
                 timeout_seconds=5)
        finally:
            if watch:
                watch_stop_event.set()

        if thread:
            thread.join()


class TestWatchFixuid:
    @pytest.mark.parametrize("watch", [
        True,
        False
    ])
    def test_watch_fixuid_order_1(self, project_loader, watch):
        project_loader("watch-fixuid")

        thread, watch_stop_event, watch_started_event, main_runner = init_test_watch(watch, ["configure"])

        try:
            os.makedirs(os.path.join(".docker", "db"), exist_ok=True)

            shutil.copy2(os.path.join("..", "files", ".docker", "db", "Dockerfile.jinja"),
                         os.path.join(".docker", "db", "Dockerfile.jinja"))
            assert os.path.exists(os.path.join(".docker", "db", "Dockerfile.jinja"))

            shutil.copy2(os.path.join("..", "files", ".docker", "db", "fixuid.yml"),
                         os.path.join(".docker", "db", "fixuid.yml"))
            assert os.path.exists(os.path.join(".docker", "db", "fixuid.yml"))

            shutil.copy2(os.path.join("..", "files", "docker-compose.yml.jsonnet"),
                         "docker-compose.yml.jsonnet")
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
                watch_stop_event.set()

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

        thread, watch_stop_event, watch_started_event, main_runner = init_test_watch(watch, ["configure"])

        try:
            os.makedirs(os.path.join(".docker", "db"), exist_ok=True)

            for f in files:
                shutil.copy2(os.path.join("..", "files", f), f)
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
                watch_stop_event.set()

        if thread:
            thread.join()
