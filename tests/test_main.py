# -*- coding: utf-8 -*-

from ddb.__main__ import main


def test_main_no_args():
    main([])


def test_main_features():
    main(["features"])


def test_main_config():
    main(["config"])


def test_main_config_variables():
    main(["config", "--variables"])
