# -*- coding: utf-8 -*-
import os
import pathlib

import zgitignore

from ddb.action import Action
from ddb.action.action import EventBinding
from ddb.config import config
from ddb.context import context
from ddb.utils.file import force_remove


class UpdateGitignoreAction(Action):
    """
    Append generated files to .gitignore
    """

    @property
    def name(self) -> str:
        return "git:update-gitignore"

    @property
    def event_bindings(self):
        return ("file:generated",
                EventBinding("file:deleted", self.remove))

    @staticmethod
    def find_gitignores(target: str):
        """
        Find writable .gitignore files, walking directories up to project home.
        """
        dirname = target

        while os.path.abspath(dirname) != os.path.abspath(config.paths.project_home):
            dirname = os.path.dirname(dirname)
            gitignore = os.path.join(dirname, ".gitignore")
            if os.path.exists(gitignore) and os.access(gitignore, os.W_OK):
                yield gitignore

    @staticmethod
    def is_file_ignored(file: str, gitignores=None):
        """Check if a file is ignored, going throw all provided gitignore files"""
        if not gitignores:
            gitignores = UpdateGitignoreAction.find_gitignores(file)

        for gitignore in gitignores:
            with open(gitignore, "r", encoding="utf-8") as gitignore_file:
                gitignore_content = gitignore_file.read().splitlines()

            inversed_gitignore_content = []
            for pattern in gitignore_content:
                if pattern.startswith("!"):
                    inversed_gitignore_content.append(pattern[1:])

            relative_file = os.path.normpath(os.path.relpath(file, os.path.dirname(gitignore)))

            zgitignore_helper = zgitignore.ZgitIgnore(gitignore_content)
            inversed_zgitignore_helper = zgitignore.ZgitIgnore(inversed_gitignore_content)
            if zgitignore_helper.is_ignored(relative_file) or inversed_zgitignore_helper.is_ignored(relative_file):
                return True, relative_file, gitignore, gitignore_content
        return False, None, None, None

    @staticmethod
    def remove(file: str):
        """
        Remove an ignored file
        :param file:
        :return:
        """
        ignored, relative_file, gitignore, gitignore_content = UpdateGitignoreAction.is_file_ignored(file)
        if not ignored:
            return

        new_gitignore_content = list(filter(lambda line: relative_file != line, gitignore_content))

        if new_gitignore_content:
            with open(gitignore, "w", encoding="utf-8") as gitignore_file:
                for line in new_gitignore_content:
                    gitignore_file.write(line)
                    gitignore_file.write("\n")
        else:
            force_remove(gitignore)

        context.log.warning("%s removed from %s", file, gitignore)

    @staticmethod
    def execute(target: str, source: str = None):
        """
        Execute action
        """
        ignored, _, _, _ = UpdateGitignoreAction.is_file_ignored(target)
        if ignored:
            return

        try:
            gitignore = next(UpdateGitignoreAction.find_gitignores(target))
        except StopIteration:
            gitignore = ".gitignore"

        relative_target = pathlib.Path(os.path.relpath(target, os.path.dirname(gitignore))).as_posix()
        UpdateGitignoreAction.append_to_block(gitignore, relative_target)
        context.log.success("%s added to %s", relative_target, gitignore)

    @staticmethod
    def append_to_block(gitignore: str, relative_target: str):
        # Retrieval of file content
        gitignore_file_content = ''
        if os.path.exists(gitignore):
            with open(gitignore, "r+", encoding="utf-8") as gitignore_file:
                gitignore_file_content = gitignore_file.read()

        # Retrieval of the current block
        current_block = UpdateGitignoreAction.get_block(gitignore_file_content)
        is_block_present = (len(current_block) > 0)

        # Creation of the new block version
        if not is_block_present:
            new_block = [UpdateGitignoreAction.get_block_limit(True), UpdateGitignoreAction.get_block_limit(False)]
        else:
            new_block = current_block.copy()

        # Addition of the target_file to the block
        new_block.insert(len(current_block) - 1, relative_target)

        # Updating the gitignore content
        if is_block_present:
            gitignore_file_content = gitignore_file_content.replace('\n'.join(current_block), '\n'.join(new_block))
        else:
            if len(gitignore_file_content) > 0:
                gitignore_file_content += '\n'
            gitignore_file_content += '\n'.join(new_block) + '\n'

        # Writing new content to the file
        with open(gitignore, "w+", encoding="utf-8") as gitignore_file:
            gitignore_file.write(gitignore_file_content)

    @staticmethod
    def get_block(gitignore_file_content: str):
        started = False
        ended = False
        lines = []
        for line in gitignore_file_content.split('\n'):
            if line == UpdateGitignoreAction.get_block_limit(True):
                started = True
            if started and not ended:
                lines.append(line)
            if line == UpdateGitignoreAction.get_block_limit(False):
                ended = True

        return lines

    @staticmethod
    def get_block_limit(start: bool):
        repository = "gfi-centre-ouest/docker-devbox"
        if start:
            return '###> {} ###'.format(repository)
        return '###< {} ###'.format(repository)
