# -*- coding: utf-8 -*-
import pytest

from ddb.__main__ import main, ParseCommandLineException


def test_main_no_args():
    with pytest.raises(ParseCommandLineException) as exc:
        main([])


def test_main_features():
    main(["features"])


def test_main_config():
    main(["config"])


def test_main_config_variables():
    main(["config", "--variables"])
