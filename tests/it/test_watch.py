import os
import threading
from pathlib import Path

from waiting import wait

from ddb.__main__ import main


class TestWatch:
    def test_watch_file_change(self, project_loader):
        project_loader("watch1")

        watch_stop_event = threading.Event()
        watch_started_event = threading.Event()
        d = threading.Thread(name='watch',
                             target=lambda: main((["--watch", "configure"]), watch_started_event, watch_stop_event))
        d.start()

        try:
            watch_started_event.wait(30)
            assert os.path.exists("test.txt")

            with open("test.txt.jinja", "w") as template_file:
                template_file.write("This is {{core.project.name}} project. (modified)")

            wait(lambda: os.path.exists('test.txt') and
                         Path('test.txt').read_text() == "This is watch1 project. (modified)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists('.gitignore') and
                         Path('.gitignore').read_text() == "test.txt\n",
                 timeout_seconds=5)
        finally:
            watch_stop_event.set()

        d.join()

    def test_watch_file_created(self, project_loader):
        project_loader("watch1")

        watch_stop_event = threading.Event()
        watch_started_event = threading.Event()
        d = threading.Thread(name='watch',
                             target=lambda: main((["--watch", "configure"]), watch_started_event, watch_stop_event))
        d.start()

        try:
            watch_started_event.wait(30)
            assert os.path.exists("test.txt")

            with open("test.created.txt.jinja", "w") as template_file:
                template_file.write("This is {{core.project.name}} project. (created)")

            wait(lambda: os.path.exists('test.created.txt') and
                         Path('test.created.txt').read_text() == "This is watch1 project. (created)",
                 timeout_seconds=5)

            wait(lambda: os.path.exists('.gitignore') and
                         Path('.gitignore').read_text() == "test.txt\ntest.created.txt\n",
                 timeout_seconds=5)
        finally:
            watch_stop_event.set()

        d.join()

    def test_watch_file_delete(self, project_loader):
        project_loader("watch1")

        watch_stop_event = threading.Event()
        watch_started_event = threading.Event()
        d = threading.Thread(name='watch',
                             target=lambda: main((["--watch", "configure"]), watch_started_event, watch_stop_event))
        d.start()

        try:
            watch_started_event.wait(30)
            assert os.path.exists("test.txt")

            os.remove("test.txt.jinja")

            wait(lambda: not os.path.exists('test.txt'), timeout_seconds=5)
            wait(lambda: not os.path.exists('.gitignore'), timeout_seconds=5)
        finally:
            watch_stop_event.set()

        d.join()

    def test_watch_file_move(self, project_loader):
        project_loader("watch1")

        watch_stop_event = threading.Event()
        watch_started_event = threading.Event()
        d = threading.Thread(name='watch',
                             target=lambda: main((["--watch", "configure"]), watch_started_event, watch_stop_event))
        d.start()

        try:
            watch_started_event.wait(30)
            assert os.path.exists("test.txt")

            os.rename("test.txt.jinja", "test2.txt.jinja")

            wait(lambda: not os.path.exists('test.txt') and os.path.exists('test2.txt') and "This is watch1 project.",
                 timeout_seconds=5)

            wait(lambda: os.path.exists('.gitignore') and
                         Path('.gitignore').read_text() == "test2.txt\n",
                 timeout_seconds=5)
        finally:
            watch_stop_event.set()

        d.join()
