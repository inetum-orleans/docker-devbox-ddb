import os
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from pytest_mock import MockerFixture

from ddb import __version__
from ddb.__main__ import main


class TestCore:
    bin = './bin/ddb'

    def test_self_update_no_binary(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: False)

        project_loader("empty")

        main(["self-update"])

        assert Path('./bin/ddb').read_bytes() == b"binary"

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == ('ddb is running from a package mode than doesn\'t support self-update.\n'
                              'You can download binary package supporting it from github: '
                              'https://github.com/inetum-orleans/docker-devbox-ddb/releases\n')

    def test_self_update_up_to_date(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_latest_release_version', lambda *args, **kwargs: __version__)

        project_loader("empty")

        main(["self-update"])

        assert Path('./bin/ddb').read_bytes() == b"binary"

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == 'ddb is already up to date.\n'

    def test_self_update_outdated(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_latest_release_version', lambda *args, **kwargs: '1.10.0')
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.9.2')

        project_loader("empty")

        main(["self-update"])

        assert Path('./bin/ddb').read_bytes() != b"binary"

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == 'A new version is available: 1.10.0\nddb has been updated.\n'

    @pytest.mark.skip("Should be enabled after 1.10.0 release")
    def test_self_update_up_to_date_force(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_latest_release_version', lambda *args, **kwargs: '1.10.0')
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.9.2')

        project_loader("empty")

        main(["self-update", "--force"])

        assert Path('./bin/ddb').read_bytes() != b"binary"

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == 'ddb is already up to date.\nddb has been updated.\n'

    def test_self_update_up_to_date(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_latest_release_version', lambda *args, **kwargs: '1.3.0')
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.3.0')

        project_loader("empty")

        main(["self-update"])

        assert Path('./bin/ddb').read_bytes() == b"binary"

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == 'ddb is already up to date.\n'

    def test_version_up_to_date(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_latest_release_version', lambda *args, **kwargs: '1.3.0')
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.3.0')

        project_loader("empty")

        main(["--version"])

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == '''+------------------------------------------------------------+
|                         ddb 1.3.0                          |
+------------------------------------------------------------+
|        Please report any bug or feature request at         |
| https://github.com/inetum-orleans/docker-devbox-ddb/issues |
+------------------------------------------------------------+\n'''

    def test_version_outdated_binary(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_binary_path', lambda *args, **kwargs: self.bin)
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_latest_release_version', lambda *args, **kwargs: '1.3.1')
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.3.0')

        project_loader("empty")

        main(["--version"])

        outerr = capsys.readouterr()
        assert outerr.err == ""
        assert outerr.out == '''+-------------------------------------------------------------------------------------+
|                                      ddb 1.3.0                                      |
+-------------------------------------------------------------------------------------+
|                          A new version is available: 1.3.1                          |
+-------------------------------------------------------------------------------------+
|                      run "ddb self-update" command to update.                       |
|                  For more information, check the following links:                   |
|       https://github.com/inetum-orleans/docker-devbox-ddb/releases/tag/1.3.1        |
| https://github.com/inetum-orleans/docker-devbox-ddb/releases/tag/1.3.1/CHANGELOG.md |
+-------------------------------------------------------------------------------------+
|                     Please report any bug or feature request at                     |
|             https://github.com/inetum-orleans/docker-devbox-ddb/issues              |
+-------------------------------------------------------------------------------------+\n'''

    def test_required_version_eq(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.3.0')

        project_loader("required-version")

        exceptions = main(["configure"])

        assert not exceptions
        assert os.path.exists('test')

    def test_required_version_lt(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.2.9')

        project_loader("required-version")

        exceptions = main(["configure"])
        assert len(exceptions) == 1
        assert str(exceptions[0]) == "This project requires ddb 1.3.0+. Current version is 1.2.9."

        outerr = capsys.readouterr()
        assert "This project requires ddb 1.3.0+. Current version is 1.2.9." in outerr.err
        assert outerr.out == ""

        assert not os.path.exists('test')

    def test_required_version_lt_binary(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.is_binary', lambda *args, **kwargs: True)
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.2.9')

        project_loader("required-version")

        exceptions = main(["configure"])
        assert len(exceptions) == 1
        assert str(exceptions[0]) == "This project requires ddb 1.3.0+. " \
                                     "Current version is 1.2.9. " \
                                     "run \"ddb self-update\" command to update."

        outerr = capsys.readouterr()
        assert "This project requires ddb 1.3.0+. Current version is 1.2.9." in outerr.err
        assert outerr.out == ""

        assert not os.path.exists('test')

    def test_required_version_gt(self, project_loader, capsys: CaptureFixture, mocker: MockerFixture):
        mocker.patch('ddb.feature.core.actions.get_current_version', lambda *args, **kwargs: '1.3.1')

        project_loader("required-version")

        exceptions = main(["configure"])

        assert not exceptions
        assert os.path.exists('test')
