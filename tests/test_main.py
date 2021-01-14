# -*- coding: utf-8 -*-
import pytest
from _pytest.capture import CaptureFixture

from ddb.__main__ import main, ParseCommandLineException


def test_main_no_args(project_loader):
    project_loader("no-config")
    with pytest.raises(ParseCommandLineException) as exc:
        main([])


def test_main_features(project_loader):
    project_loader("no-config")
    main(["features"])


def test_main_config(project_loader):
    project_loader("no-config")
    main(["config"])


def test_main_config_should_display_error(project_loader, capsys: CaptureFixture):
    project_loader("no-config")
    main(["configure"])

    outerr = capsys.readouterr()
    assert not outerr.out
    assert "No project configuration file found." in outerr.err


def test_main_config_variables(project_loader):
    project_loader("no-config")
    main(["config", "--variables"])
