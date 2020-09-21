# -*- coding: utf-8 -*-
from subprocess import CalledProcessError
from typing import ClassVar, Iterable

from dotty_dict import Dotty

from ddb.feature import Feature
from .schema import VersionSchema
from ...utils.process import run


def is_git_repository():
    """
    Check if git command line is available, and if a git repository index is available in current directory
    """
    try:
        run("git", "rev-parse", "--git-dir")
        return True
    except CalledProcessError:
        return False


def get_tag_from_vcs():
    """
    Get last tag from git index
    """
    try:
        return run("git", "describe", "--tags", "--abbrev=0").decode("utf-8").strip()
    except CalledProcessError as exc:
        if exc.returncode == 128:
            return None
        raise


def get_branch_from_vcs():
    """
    Get branch name from git index
    """
    try:
        branch = run("git", "rev-parse", "--abbrev-ref", "HEAD").decode("utf-8").strip()
    except CalledProcessError as exc:
        if exc.returncode == 128:
            return None
        raise

    if branch == "HEAD":
        # CI checkout a commit hash, making the HEAD detached.
        try:
            refs = run("git", "for-each-ref", "--format=%(refname:short)", "refs/heads") \
                .decode("utf-8").strip()

            if refs:
                refs_split = refs.splitlines()
                if refs_split:
                    return refs_split[0]
        except CalledProcessError as exc:
            if exc.returncode == 128:
                return branch
            raise

        # CI may not checkout branches locally, so try with remote origin
        try:
            remote = 'origin'
            refs = run("git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/" + remote) \
                .decode("utf-8").strip()

            if refs:
                refs_split = refs.splitlines()
                if refs_split:
                    value = refs_split[0]
                    if value.startswith(remote + '/'):
                        return value[len(remote + 'origin/'):]
        except CalledProcessError as exc:
            if exc.returncode == 128:
                return branch
            raise

    return branch


def get_version_from_vcs():
    """
    Get version from git index
    """
    try:
        return run("git", "describe", "--tags").decode("utf-8").strip()
    except CalledProcessError as exc:
        if exc.returncode == 128:
            return None
        raise


def get_hash_from_vcs():
    """
    Get commit hash from git index
    """
    try:
        return run("git", "rev-parse", "HEAD").decode("utf-8").strip()
    except CalledProcessError as exc:
        if exc.returncode == 128:
            return None
        raise


def get_short_hash_from_vcs():
    """
    Get commit short hash from git index
    """
    try:
        return run("git", "log", "--pretty=format:%h", "-n", "1").decode("utf-8").strip()
    except CalledProcessError as exc:
        if exc.returncode == 128:
            return None
        raise


class VersionFeature(Feature):
    """
    Update gitignore files when a file is generated.
    """

    @property
    def name(self) -> str:
        return "version"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> ClassVar[VersionSchema]:
        return VersionSchema

    def _configure_defaults(self, feature_config: Dotty):
        if not is_git_repository():
            return

        branch = feature_config.get("branch")
        if branch is None:
            branch = get_branch_from_vcs()
            feature_config["branch"] = branch

        version = feature_config.get("version")
        if version is None:
            version = get_version_from_vcs()
            feature_config["version"] = version

        tag = feature_config.get("tag")
        if tag is None:
            tag = get_tag_from_vcs()
            feature_config["tag"] = tag

        hash_value = feature_config.get("hash")
        if hash_value is None:
            hash_value = get_hash_from_vcs()
            feature_config["hash"] = hash_value

        short_hash = feature_config.get("short_hash")
        if short_hash is None:
            short_hash = get_short_hash_from_vcs()
            feature_config["short_hash"] = short_hash
