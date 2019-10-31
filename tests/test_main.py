# -*- coding: utf-8 -*-

from ddb.__main__ import main


def test_main_no_args():
    main([])


def test_main_info():
    main(["info"])
