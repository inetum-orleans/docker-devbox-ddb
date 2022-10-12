# -*- coding: utf-8 -*-
import fnmatch
import os
import re
import shutil
from pathlib import Path
from tempfile import gettempdir, NamedTemporaryFile
from typing import List, Union, Optional, Tuple

import chmod_monkey
import requests
from braceexpand import braceexpand

from ddb.config import config
from ddb.context import context
from ddb.utils.re import build_or_pattern


def has_same_content(filename1: str, filename2: str, read_mode='rb') -> bool:
    """
    Check if the content of two files are same
    """
    with open(filename1, mode=read_mode) as file1:  # pylint:disable=unspecified-encoding
        with open(filename2, mode=read_mode) as file2:  # pylint:disable=unspecified-encoding
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


def force_remove(file: str, silent=False):
    """
    Remove a file, trying to unset readonly flag if a PermissionError occurs.
    """
    try:
        os.remove(file)
    except PermissionError:
        # On windows, removing a readonly file raise this error.
        chmod(file, '+w', logging=False)
        os.remove(file)
    except FileNotFoundError:
        if not silent:
            context.log.warning("%s can't be removed because it's already absent", file)


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


class FileUtils:
    """
    Some file management functions
    """

    @staticmethod
    def get_file_content(url: str) -> str:
        """
        Get the content of the file
        :param url: the path to the file (https? or file)
        :return:
        """
        if url.startswith('file://'):
            return FileUtils._get_local_file_content(url)
        return requests.get(url).text

    @staticmethod
    def _get_local_file_content(file_path: str) -> str:
        """
        Get the content of the file
        :param file_path: the path to the file (absolute or relative)
        :return:
        """
        file_path = file_path.replace('file://', '')
        if not os.path.isabs(file_path):
            file_path = os.path.join(config.path.project_home, file_path)
        with open(file_path, 'rb') as file:
            return file.read().decode("utf-8")


# pylint:disable=too-many-instance-attributes
class FileWalker:
    """
    Walk files inside project directory.
    TODO: Add a excludes_from_gitignore option to automatically exclude files based on gitignore behavior.
    """

    # pylint:disable=too-many-arguments
    def __init__(self,
                 includes: Optional[List[str]],
                 excludes: Optional[List[str]],
                 include_files: Optional[List[str]],
                 exclude_files: Optional[List[str]],
                 suffixes: Optional[List[str]],
                 rootpath: Optional[Union[Path, str]] = None,
                 recursive=True,
                 skip_processed_sources=True,
                 skip_processed_targets=True):
        if includes is None:
            includes = []
        if excludes is None:
            excludes = []
        if include_files is None:
            include_files = []
        if exclude_files is None:
            exclude_files = []
        includes = self._braceexpand(includes)
        excludes = self._braceexpand(excludes)
        include_files = self._braceexpand(include_files)
        exclude_files = self._braceexpand(exclude_files)
        self.includes = [FileWalker.re_compile_patterns(includes)] if includes else []
        self.excludes = [
            re.compile(
                build_or_pattern([fnmatch.translate(x) for x in excludes]))] if excludes else []
        self.include_files = [
            re.compile(build_or_pattern([fnmatch.translate(x) for x in include_files]))] if include_files else []
        self.exclude_files = [
            re.compile(build_or_pattern([fnmatch.translate(x) for x in exclude_files]))] if exclude_files else []
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

    def _do_yield(self, source):
        yield source

    def _walk(self, path, recursive=True):
        for root, dirs, files in os.walk(path):
            context.log.debug('%s', root)
            for dirs_item in list(dirs):
                dirpath = FileWalker._join(root, dirs_item)
                if self._is_included(dirpath, *self.includes) and \
                        not self._is_excluded(dirpath, *self.excludes):
                    yield dirpath
                else:
                    context.log.debug('%s [ignored]', dirpath)
                    dirs.remove(dirs_item)

            for files_item in list(files):
                filepath = FileWalker._join(root, files_item)
                if self._is_included(filepath, *self.include_files) and \
                        not self._is_excluded(filepath, *self.exclude_files):
                    yield filepath

            if not recursive:
                break

    def is_source_filtered(self, candidate: str):
        """
        Check if a source path is filtered out by includes/excludes
        """
        return not self._is_included(candidate, *self.include_files) or \
               self._is_excluded(candidate, *self.exclude_files) or \
               self._has_ancestor_excluded(Path(candidate), *self.excludes)

    @staticmethod
    def _braceexpand(expressions):
        expanded_expressions = []
        for expression in expressions:
            expanded_expressions.extend(braceexpand(expression))

        return expanded_expressions

    @staticmethod
    def _is_excluded(candidate: str, *excludes: re.Pattern) -> bool:
        if not excludes:
            return False
        return FileWalker.match_any_pattern(candidate, *excludes)

    @staticmethod
    def _is_included(candidate: str, *includes: re.Pattern) -> bool:
        if not includes:
            return True
        return FileWalker.match_any_pattern(candidate, *includes)

    @staticmethod
    def _has_ancestor_excluded(candidate_path: Path, *excludes: re.Pattern) -> bool:
        while True:
            if FileWalker._is_excluded(str(candidate_path), *excludes):
                return True
            candidate_path_parent = candidate_path.parent
            if not candidate_path_parent or candidate_path_parent == candidate_path:
                break
            candidate_path = candidate_path_parent
        return False

    @staticmethod
    def _path_alternatives_for_pattern_match(path: str):
        if path[0:2] == './':
            yield path[2:]
            yield path
        else:
            yield path
            yield './' + path

    @staticmethod
    def _as_posix_fast(path: str):
        return path.replace('\\', '/')

    @staticmethod
    def _join(parent: str, child: str):
        return os.path.join(parent, child) if parent != '.' else child

    @staticmethod
    def re_compile_patterns(*patterns: List[str]):
        """
        Compile a list of string containing patterns to regexp
        """
        return re.compile(build_or_pattern([fnmatch.translate(pattern) for pattern in patterns]))

    @staticmethod
    def match_any_pattern(candidate: str, *patterns: re.Pattern):
        """
        Check if a string match at least one of provided compiled pattern
        """
        candidate = FileWalker._as_posix_fast(candidate)
        for pattern in patterns:
            for candidate_alternative in FileWalker._path_alternatives_for_pattern_match(candidate):
                if pattern.match(candidate_alternative):
                    return True
        return False

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
            if source in context.processed_sources:
                return None

        target, suffix = self._get_target_and_suffix(source, self.suffixes)

        if self.skip_processed_targets:
            if target in context.processed_targets:
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


def get_single_temporary_file_directory(*args):
    """
    Get directory for SingleTemporaryFile *args.
    """
    return os.path.join(gettempdir(), *args)


class SingleTemporaryFile:
    """
    A NamedTemporaryFile wrapper that is created in tmp subdirectory joined with *args strings, using options from
     **kwargs. It will keep only the last temporary file is subdirectory by cleaning up the directory on each call.
    """

    def __init__(self, *args, **kwargs):
        self.tempdir = get_single_temporary_file_directory(*args)
        os.makedirs(self.tempdir, exist_ok=True)

        if "dir" in kwargs:
            kwargs.pop("dir")
        if "delete" in kwargs:
            kwargs.pop("delete")

        # pylint:disable=consider-using-with
        self.named_temporary_file = NamedTemporaryFile(dir=self.tempdir, delete=False, **kwargs)

    def __enter__(self):
        return self.named_temporary_file.__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        tmp_filepath = self.named_temporary_file.name
        try:
            return self.named_temporary_file.__exit__(exc_type, exc_value, exc_traceback)
        finally:
            for previous_temporary_file in os.listdir(self.tempdir):
                previous_temporary_filepath = os.path.join(self.tempdir, previous_temporary_file)
                if previous_temporary_filepath != tmp_filepath:
                    os.remove(previous_temporary_filepath)
