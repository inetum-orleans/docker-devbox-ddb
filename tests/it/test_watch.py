import os
import threading
from pathlib import Path
from typing import Iterable

import pytest
from waiting import wait

from ddb.__main__ import main
from tests.utilstest import compare_gitignore_generated


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
        thread = threading.Thread(name='watch',
                                  target=main_runner)
        thread.start()
        watch_started_event.wait(30)
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

            wait(lambda: os.path.exists('test.txt') and
                         Path('test.txt').read_text() == "This is watch1 project. (modified)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists('.gitignore') and
                         compare_gitignore_generated(Path('.gitignore').read_text(), 'test.txt'),
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

            wait(lambda: os.path.exists('test.created.txt') and
                         Path('test.created.txt').read_text() == "This is watch1 project. (created)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists('.gitignore') and
                         compare_gitignore_generated(Path('.gitignore').read_text(), 'test.txt', 'test.created.txt'),
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

            wait(lambda: not os.path.exists('test.txt'), timeout_seconds=5)
            wait(lambda: not os.path.exists('.gitignore'), timeout_seconds=5)
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

            wait(lambda: not os.path.exists('test.txt') and os.path.exists('test2.txt') and "This is watch1 project.",
                 timeout_seconds=5)

            wait(lambda: os.path.exists('.gitignore') and
                         compare_gitignore_generated(Path('.gitignore').read_text(), 'test2.txt'),
                 timeout_seconds=5)
        finally:
            if watch:
                watch_stop_event.set()

        if thread:
            thread.join()
