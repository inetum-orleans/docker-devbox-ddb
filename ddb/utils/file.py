# -*- coding: utf-8 -*-


def has_same_content(filename1: str, filename2: str) -> bool:
    """
    Check if the content of two files are same
    """
    with open(filename1, 'rb') as file1:
        with open(filename2, 'rb') as file2:
            return file1.read() == file2.read()
