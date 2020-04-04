# -*- coding: utf-8 -*-
import os
from typing import Union, Iterable

import zgitignore

from ddb.action import Action


def find_gitignore(target: str):
    """
    Find the nearest writable .gitignore file, walking directories up to cwd.
    """
    dirname = target
    while os.path.abspath(dirname) != os.path.abspath(os.getcwd()):
        dirname = os.path.dirname(dirname)
        gitignore = os.path.join(dirname, ".gitignore")
        if os.path.exists(gitignore) and os.access(gitignore, os.W_OK):
            return gitignore

    return None


class UpdateGitignoreAction(Action):
    """
    Append generated files to .gitignore
    """

    @property
    def name(self) -> str:
        return "git:update-gitignore"

    @property
    def event_bindings(self) -> Union[str, Iterable[Union[Iterable[str], str]]]:
        return "event:file-generated"

    def execute(self, *args, **kwargs):
        target = kwargs.pop("target")

        gitignore = find_gitignore(target)
        if not gitignore:
            gitignore = ".gitignore"
            gitignore_content = []
        else:
            with open(gitignore, "r", encoding="utf-8") as gitignore_file:
                gitignore_content = gitignore_file.readlines()

        inversed_gitignore_content = []
        for pattern in gitignore_content:
            if pattern.startswith("!"):
                inversed_gitignore_content.append(pattern[1:])

        zgitignore_helper = zgitignore.ZgitIgnore(gitignore_content)
        inversed_zgitignore_helper = zgitignore.ZgitIgnore(inversed_gitignore_content)
        if not zgitignore_helper.is_ignored(target) and not inversed_zgitignore_helper.is_ignored(target):
            with open(gitignore, "a", encoding="utf-8") as gitignore_file:
                if gitignore_content and gitignore_content[-1].strip():
                    gitignore_file.write(os.linesep)
                gitignore_file.write(os.path.normpath(target))
