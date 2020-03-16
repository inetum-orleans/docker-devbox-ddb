# -*- coding: utf-8 -*-
import fnmatch
import os
from pathlib import Path
from typing import List, Union, Optional

from braceexpand import braceexpand


def has_same_content(filename1: str, filename2: str) -> bool:
    """
    Check if the content of two files are same
    """
    with open(filename1, 'rb') as file1:
        with open(filename2, 'rb') as file2:
            return file1.read() == file2.read()


class TemplateFinder:
    """
    Find templates sources inside project directory.
    """

    # pylint:disable=too-many-arguments
    def __init__(self, includes: List[str], excludes: List[str], suffixes: List[str],
                 rootpath: Union[Path, str] = Path('.'), recursive=True,
                 first_only=True):
        self.includes, self.excludes = self._braceexpand(includes, excludes)
        self.suffixes = suffixes
        self.rootpath = rootpath if isinstance(rootpath, Path) else Path(rootpath)
        self.recursive = recursive
        self.first_only = first_only

    @property
    def templates(self):
        """
        Yields over a tuple (template, target) with found templates.
        """

        processed = set()

        for source in self._walk(str(self.rootpath), recursive=self.recursive):
            target = self._get_target(source, self.suffixes)

            if self.first_only:
                if target in processed:
                    continue
                processed.add(target)

            if target:
                yield source, target

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

            ordered_files = []
            for expand_include in self.includes:
                for files_item in list(files):
                    filepath = os.path.join(root, files_item)
                    if self._is_included(filepath, expand_include) and \
                            not self._is_excluded(filepath, *self.excludes):
                        ordered_files.append(filepath)

            for filepath in ordered_files:
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
        for exclude in excludes:
            if fnmatch.fnmatch(candidate, exclude) or fnmatch.fnmatch(os.path.normpath(candidate), exclude):
                excluded = True
                break
        return excluded

    @staticmethod
    def _is_included(candidate: str, *includes: List[str]) -> bool:
        included = False
        for includes in includes:
            if fnmatch.fnmatch(candidate, includes) or fnmatch.fnmatch(os.path.normpath(candidate), includes):
                included = True
                break
        return included

    @staticmethod
    def _get_target(template_candidate: str, suffixes: List[str]) -> Optional[str]:
        basename, ext = os.path.splitext(template_candidate)
        if ext in suffixes:
            return basename

        if not ext and basename.startswith("."):
            ext = basename
            basename = ""

        for suffix in suffixes:
            if basename.endswith(suffix):
                return template_candidate[:len(basename) - len(suffix)] + ext

        return None

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
            return ["**/*{" + joined_suffixes + "}" + extensions_pattern]
        return ["**/*" + suffixes[0] + extensions_pattern]
