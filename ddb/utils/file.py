# -*- coding: utf-8 -*-
import fnmatch
import os
import re
import shutil
from pathlib import Path
from typing import List, Union, Optional, Tuple

import chmod_monkey
from braceexpand import braceexpand

from ddb.config import config
from ddb.context import context


def has_same_content(filename1: str, filename2: str, read_mode='rb') -> bool:
    """
    Check if the content of two files are same
    """
    with open(filename1, mode=read_mode) as file1:
        with open(filename2, mode=read_mode) as file2:
            return file1.read() == file2.read()


def write_if_different(file, data, read_mode='r', write_mode='w', log_source=None, readonly=True, **kwargs) -> bool:
    """
    Write the file if existing data is different than given data.
    """
    try:
        read_encoding = "utf-8" if 'b' not in read_mode else None  # TODO: make default encoding configurable
        write_encoding = "utf-8" if 'b' not in write_mode else None

        if os.path.exists(file):
            try:
                with open(file, mode=read_mode, encoding=read_encoding, **kwargs) as read_file:
                    existing_data = read_file.read()
            except OSError:
                shutil.rmtree(file)
                existing_data = None
        else:
            existing_data = None

        if existing_data == data:
            context.log.notice("%s -> %s", log_source if log_source else "", file)
            return False

        if not os.access(file, os.W_OK) and os.path.isfile(file):
            chmod(file, '+w', logging=False)
        with open(file, mode=write_mode, encoding=write_encoding, **kwargs) as write_file:
            write_file.write(data)

        context.log.success("%s -> %s", log_source if log_source else "", file)

        return True
    finally:
        if readonly and os.path.isfile(file):
            chmod(file, '+r', logging=False)


def copy_if_different(source, target, read_mode='r', write_mode='w', log=False, readonly=True, **kwargs) -> bool:
    """
    Copy source to target if existing source data is different than target data.
    """
    try:
        read_encoding = "utf-8" if 'b' not in read_mode else None  # TODO: make default encoding configurable
        write_encoding = "utf-8" if 'b' not in write_mode else None

        if os.path.exists(source):
            with open(source, mode=read_mode, encoding=read_encoding, **kwargs) as read_file:
                source_data = read_file.read()
        else:
            source_data = None

        if os.path.exists(target):
            with open(target, mode=read_mode, encoding=read_encoding, **kwargs) as read_file:
                target_data = read_file.read()
        else:
            target_data = None

        if source_data == target_data:
            if log:
                context.log.notice("%s -> %s", source, target)
            return False

        if not os.access(target, os.W_OK) and os.path.exists(target):
            chmod(target, '+w')
        with open(target, mode=write_mode, encoding=write_encoding, **kwargs) as write_file:
            write_file.write(source_data)

        if log:
            context.log.success("%s -> %s", source, target)

        return True
    finally:
        if readonly and os.path.isfile(target):
            chmod(target, '+r', logging=False)


def force_remove(file: str):
    """
    Remove a file, trying to unset readonly flag if a PermissionError occurs.
    """
    try:
        os.remove(file)
    except PermissionError:
        # On windows, removing a readonly file raise this error.
        chmod(file, '+w', logging=False)
        os.remove(file)


def chmod(file: str, mode: str, logging=True):
    """
    Apply given mode to file
    """
    new_mode, old_mode = chmod_monkey.to_mode(file, mode, return_old_mode=True)
    if old_mode != new_mode:
        if logging:
            context.log.success("chmod %s %s", mode, file)
        os.chmod(file, new_mode)
    else:
        if logging:
            context.log.notice("chmod %s %s", mode, file)


class FileWalker:
    """
    Walk files inside project directory.
    TODO: Add a excludes_from_gitignore option to automatically exclude files based on gitignore behavior.
    """

    # pylint:disable=too-many-arguments
    def __init__(self,
                 includes: Optional[List[str]],
                 excludes: Optional[List[str]],
                 suffixes: Optional[List[str]],
                 rootpath: Optional[Union[Path, str]] = None,
                 recursive=True,
                 skip_processed_sources=True,
                 skip_processed_targets=True):
        if includes is None:
            includes = []
        if excludes is None:
            excludes = []
        includes, excludes = self._braceexpand(includes, excludes)
        self.includes = list(map(lambda x: re.compile(fnmatch.translate(x)), includes))
        self.excludes = list(map(lambda x: re.compile(fnmatch.translate(x)), excludes))
        self.suffixes = suffixes if suffixes is not None else []
        if not rootpath:
            rootpath = os.path.relpath(config.paths.project_home)
        self.rootpath = rootpath if isinstance(rootpath, Path) else Path(rootpath)
        self.recursive = recursive
        self.skip_processed_sources = skip_processed_sources
        self.skip_processed_targets = skip_processed_targets

    @property
    def items(self):
        """
        Yields over a tuple (template, target) with found templates.
        """

        for source in self._walk(str(self.rootpath), recursive=self.recursive):
            yield from self._do_yield(source)

    def _do_yield(self, source):  # pylint:disable=no-self-use
        yield source

    def _walk(self, *args, recursive=True, **kwargs):
        _walk_generator = os.walk(*args, **kwargs)
        if not recursive:
            try:
                _walk_generator = next(_walk_generator)
            except StopIteration:
                return
        for root, dirs, files in os.walk(*args, **kwargs):
            for dirs_item in list(dirs):
                dirpath = os.path.join(root, dirs_item)
                if self._is_excluded(dirpath, *self.excludes):
                    dirs.remove(dirs_item)

            for files_item in list(files):
                filepath = os.path.relpath(os.path.join(root, files_item))
                if self._is_included(filepath, *self.includes) and \
                        not self._is_excluded(filepath, *self.excludes):
                    yield filepath

    @staticmethod
    def _braceexpand(includes, excludes):
        expanded_includes = []
        for include in includes:
            expanded_includes.extend(braceexpand(include))

        expanded_excludes = []
        for exclude in excludes:
            expanded_excludes.extend(braceexpand(exclude))

        return expanded_includes, expanded_excludes

    @staticmethod
    def _is_excluded(candidate: str, *excludes: List[str]) -> bool:
        excluded = False
        if not excludes:
            return False
        # TODO find a better solution instead of adding the "./" in front of the normed path
        norm_candidate = FileWalker._prefix_path_to_current_folder(Path(os.path.normpath(candidate)).as_posix())
        for exclude in excludes:
            if exclude.match(candidate) or exclude.match(norm_candidate):
                excluded = True
                break
        return excluded

    @staticmethod
    def _prefix_path_to_current_folder(path: str):
        if path[0:2] == './':
            return path
        return './' + path

    def is_source_filtered(self, candidate: str):
        """
        Check if a source path is filtered out by includes/excludes
        """
        return not self._is_included(candidate, *self.includes) or \
               self._is_excluded(candidate, *self.excludes)

    @staticmethod
    def _is_included(candidate: str, *includes: List[str]) -> bool:
        included = False
        norm_candidate = None
        if not includes:
            return True
        for include in includes:
            if not norm_candidate:
                norm_candidate = Path(os.path.normpath(candidate)).as_posix()
            if include.match(candidate) or include.match(norm_candidate):
                included = True
                break
        return included

    @staticmethod
    def build_default_includes_from_suffixes(suffixes: List[str], extensions=(".*", "")):
        """
        Build default includes configuration from suffixes configuration.
        """
        if extensions:
            extensions_pattern = "{" + ",".join(extensions) + "}"
        else:
            extensions_pattern = ""

        if len(suffixes) > 1:
            joined_suffixes = ','.join(suffixes)
            return ["*{" + joined_suffixes + "}" + extensions_pattern]
        if len(suffixes) > 0:
            return ["*" + suffixes[0] + extensions_pattern]
        if extensions_pattern:
            return ["*" + suffixes[0] + extensions_pattern]
        return []


class TemplateFinder(FileWalker):
    """
    Find templates sources inside project directory.
    """

    def _do_yield(self, source):
        target = self.get_target(source, check=False)
        if target:
            if self.skip_processed_targets:
                if target in context.processed_targets:
                    return
            yield source, target

    def get_target(self, source, check=True):
        """
        Get the target of given source, or None if it doesn't match suffixes.
        """
        if check:
            if self.is_source_filtered(source):
                return None

        if self.skip_processed_sources:
            if source in context.processed_sources.keys():
                return None

        target, suffix = self._get_target_and_suffix(source, self.suffixes)

        if self.skip_processed_targets:
            if target in context.processed_targets.keys():
                previous_source = context.processed_targets[target]
                _, previous_suffix = self._get_target_and_suffix(previous_source, self.suffixes)
                if previous_suffix not in self.suffixes or \
                        self.suffixes.index(previous_suffix) <= self.suffixes.index(suffix):
                    return None

        return target

    @staticmethod
    def _get_target_and_suffix(template_candidate: str, suffixes: List[str]) -> Optional[Tuple[str, str]]:
        basename, ext = os.path.splitext(template_candidate)
        if ext in suffixes:
            return basename, ext

        if not ext and basename.startswith("."):
            ext = basename
            basename = ""

        for suffix in suffixes:
            if basename.endswith(suffix):
                return template_candidate[:len(basename) - len(suffix)] + ext, suffix

        return None, None
