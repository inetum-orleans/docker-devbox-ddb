# -*- coding: utf-8 -*-
import os
import pathlib
from typing import Optional, List

import zgitignore

from ddb.action.action import EventBinding, InitializableAction
from ddb.cache import caches, register_project_cache
from ddb.config import config
from ddb.context import context
from ddb.event import events
from ddb.utils.file import force_remove


class UpdateGitignoreAction(InitializableAction):
    """
    Append generated files to .gitignore
    """

    @property
    def name(self) -> str:
        return "git:update-gitignore"

    @property
    def event_bindings(self):
        return (events.file.generated,
                EventBinding(events.file.deleted, self.remove),
                EventBinding(events.phase.configure, self.enforced)
                )

    def initialize(self):
        register_project_cache("gitignore")

    def destroy(self):
        if caches.has("gitignore"):
            caches.unregister("gitignore", callback=lambda c: c.close())

    @staticmethod
    def execute(target: str, source: str = None):
        """
        Execute action
        """
        if not UpdateGitignoreAction._check_file_in_project(target):
            return

        ignored, _, _, _, _, _ = UpdateGitignoreAction._check_file_ignored(target)
        if ignored:
            return

        try:
            gitignore = next(UpdateGitignoreAction._find_gitignores(target))
        except StopIteration:
            gitignore = ".gitignore"

        relative_target = UpdateGitignoreAction._get_relative_path(target=target, gitignore=gitignore, first_slash=True)

        # Retrieve the block lines
        block_lines, before_lines, after_lines = UpdateGitignoreAction._read_and_split_gitignore_file(gitignore)

        # Add of the relative_target to the block and sort the whole block.
        if relative_target not in block_lines:
            block_lines.append(relative_target)

            UpdateGitignoreAction._sanitize_block(block_lines, before_lines, after_lines)
            UpdateGitignoreAction._write_gitignore_content(gitignore, before_lines + block_lines + after_lines)
            context.log.success("%s added to %s", relative_target, gitignore)

    @staticmethod
    def enforced():
        """
        Handle the list of enforced actions
        """
        files = config.data.get('gitignore.enforce')
        cache = caches.get("gitignore")
        cached_files = cache.get('enforced', list())

        for file in cached_files:
            if file not in files:
                UpdateGitignoreAction.remove(file)

        for file in files:
            UpdateGitignoreAction.execute(file)
            if file not in cached_files:
                cached_files.append(file)

        cache.set('enforced', cached_files)
        cache.flush()

    @staticmethod
    def remove(file: str):
        """
        Remove an ignored file
        :param file:
        :return:
        """
        ignored, target_file, gitignore, block_lines, before_lines, after_lines = \
            UpdateGitignoreAction._check_file_ignored(file)
        if not ignored:
            return

        # Removal of the target_file to the block and sort the whole block.
        if target_file in block_lines:
            block_lines.remove(target_file)

            UpdateGitignoreAction._sanitize_block(block_lines, before_lines, after_lines)
            UpdateGitignoreAction._write_gitignore_content(gitignore, before_lines + block_lines + after_lines)

            context.log.warning("%s removed from %s", file, gitignore)

    @staticmethod
    def _check_file_in_project(target):
        target_path = os.path.realpath(target)
        cwd = os.path.realpath(".")
        return target_path.startswith(cwd)

    @staticmethod
    def _get_relative_path(target: str, gitignore: str, first_slash: bool = True):
        relpath = pathlib.Path(os.path.relpath(target, os.path.dirname(gitignore))).as_posix()
        if first_slash:
            return "/" + relpath
        return relpath

    @staticmethod
    def _find_gitignores(target: str):
        """
        Find writable .gitignore files, walking directories up to project home.
        """
        dirname = target

        while os.path.abspath(dirname).startswith(config.paths.project_home) and \
                os.path.abspath(dirname) != os.path.abspath(config.paths.project_home):
            dirname = os.path.dirname(dirname)
            gitignore = os.path.join(dirname, ".gitignore")
            if os.path.exists(gitignore) and os.access(gitignore, os.W_OK):
                yield gitignore

    @staticmethod
    def _check_file_ignored(file: str, gitignores=None):
        """
        Check if a file is ignored, going throw all provided gitignore files
        :param file:
        :param gitignores:
        :return:
        """
        if not gitignores:
            gitignores = UpdateGitignoreAction._find_gitignores(file)

        for gitignore in gitignores:
            block_lines, before_lines, after_lines = UpdateGitignoreAction._read_and_split_gitignore_file(gitignore)

            gitignore_content = before_lines + block_lines + after_lines

            inversed_gitignore_content = []
            for pattern in gitignore_content:
                if pattern.startswith("!"):
                    inversed_gitignore_content.append(pattern[1:])

            relative_file = UpdateGitignoreAction._get_relative_path(file, gitignore)

            zgitignore_helper = zgitignore.ZgitIgnore(gitignore_content)
            inversed_zgitignore_helper = zgitignore.ZgitIgnore(inversed_gitignore_content)
            if zgitignore_helper.is_ignored(relative_file) or inversed_zgitignore_helper.is_ignored(relative_file):
                return True, relative_file, gitignore, block_lines, before_lines, after_lines
        return False, None, None, None, None, None

    @staticmethod
    def _get_block_limit(start: bool):
        """
        Generate the gitignore block limit
        :param start: if it is the start of the block or not
        :return:
        """
        markers = config.data.get('gitignore.markers', ['inetum-orleans/docker-devbox'])

        if start:
            return f'###> {markers[0]} ###'
        return f'###< {markers[0]} ###'

    @staticmethod
    def _is_block_limit(line: str, start: Optional[bool] = None):
        """
        Check if line match a block limit.
        :param line: line to check
        :param start: if it is the start of the block or not
        :return:
        """
        markers = config.data.get('gitignore.markers', ['inetum-orleans/docker-devbox'])

        for marker in markers:
            if start or start is None:
                if f'###> {marker} ###' == line:
                    return True
            if not start or start is None:
                if f'###< {marker} ###' == line:
                    return True
        return False

    @staticmethod
    def _write_gitignore_content(gitignore: str, content: List[str]):
        if [line for line in content if line]:
            with open(gitignore, "w", encoding="utf-8") as gitignore_file:
                for lineno, line in enumerate(content):
                    if lineno > 0:
                        gitignore_file.write('\n')
                    gitignore_file.write(line)
        else:
            force_remove(gitignore)

    @staticmethod
    def _split_block_lines(gitignore_file_content: str):
        started = False
        ended = False
        before_lines = []
        content_lines = []
        after_lines = []
        for line in gitignore_file_content.split('\n'):
            if UpdateGitignoreAction._is_block_limit(line, False):
                ended = True
            if not started and not ended:
                before_lines.append(line)
            elif started and not ended:
                content_lines.append(line)
            elif started and ended:
                after_lines.append(line)
            if UpdateGitignoreAction._is_block_limit(line, True):
                started = True

        return content_lines, before_lines, after_lines

    @staticmethod
    def _read_and_split_gitignore_file(gitignore_file: str):
        if os.path.exists(gitignore_file):
            with open(gitignore_file, "r+", encoding="utf-8") as gitignore_fp:
                return UpdateGitignoreAction._split_block_lines(gitignore_fp.read())
        else:
            return [], [], []

    @staticmethod
    def _sanitize_block(block_lines, before_lines, after_lines):
        block_lines = [line for line in block_lines if line]
        block_lines.sort()

        if block_lines:
            if not before_lines or not UpdateGitignoreAction._is_block_limit(before_lines[-1], start=True):
                before_lines.append(UpdateGitignoreAction._get_block_limit(start=True))

            if not after_lines or not UpdateGitignoreAction._is_block_limit(after_lines[0], start=False):
                after_lines.insert(0, UpdateGitignoreAction._get_block_limit(start=False))
        else:
            if before_lines and UpdateGitignoreAction._is_block_limit(before_lines[-1], start=True):
                before_lines.pop(-1)
            if after_lines and UpdateGitignoreAction._is_block_limit(after_lines[0], start=False):
                after_lines.pop(0)
