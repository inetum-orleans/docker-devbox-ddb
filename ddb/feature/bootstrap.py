# -*- coding: utf-8 -*-
from typing import Iterable

import pkg_resources
from toposort import toposort_flatten

from . import features
from .certs import CertsFeature
from .cookiecutter import CookiecutterFeature
from .copy import CopyFeature
from .core import CoreFeature
from .docker import DockerFeature
from .feature import Feature
from .file import FileFeature
from .fixuid import FixuidFeature
from .git import GitFeature
from .gitignore import GitignoreFeature
from .jinja import JinjaFeature
from .jsonnet import JsonnetFeature
from .permissions import PermissionsFeature
from .run import RunFeature
from .shell import ShellFeature
from .smartcd import SmartcdFeature
from .symlinks import SymlinksFeature
from .traefik import TraefikFeature
from .version import VersionFeature
from .ytt import YttFeature
from ..config import config
from ..config import migrations

_default_available_features = [CertsFeature(),
                               CopyFeature(),
                               CookiecutterFeature(),
                               CoreFeature(),
                               DockerFeature(),
                               FileFeature(),
                               FixuidFeature(),
                               GitFeature(),
                               GitignoreFeature(),
                               JinjaFeature(),
                               JsonnetFeature(),
                               PermissionsFeature(),
                               RunFeature(),
                               SmartcdFeature(),
                               ShellFeature(),
                               SymlinksFeature(),
                               TraefikFeature(),
                               VersionFeature(),
                               YttFeature()]

_available_features = list(_default_available_features)


def get_sorted_features(available_features: Iterable[Feature] = None):
    """
    Register default features and setuptools entrypoint 'ddb_features' inside features registry.
    Features are registered in order for their dependency to be registered first with a topological sort.
    Withing a command phase, actions are executed in the order of their feature registration.
    """
    if available_features is None:
        available_features = _available_features

    entrypoint_features = {f.name: f for f in available_features}
    for entry_point in pkg_resources.iter_entry_points('ddb_features'):
        feature = entry_point.load()()
        entrypoint_features[feature.name] = feature

    required_dependencies, toposort_data = _prepare_dependencies_data(entrypoint_features)
    _check_missing_dependencies(entrypoint_features, required_dependencies)

    dependencies = config.data.get('dependencies')
    if dependencies:
        for feat, feat_dependencies in dependencies.items():
            if feat not in toposort_data:
                toposort_data[feat] = set()
            for feat_dependency in feat_dependencies:
                toposort_data[feat].add(feat_dependency)

    sorted_feature_names = toposort_flatten(toposort_data, sort=True)
    for feature_name in sorted_feature_names:
        feature = entrypoint_features.get(feature_name)
        if feature:
            yield feature


def _prepare_dependencies_data(entrypoint_features):
    """
    Compute required dependencies and toposort data.
    """
    required_dependencies = {}
    toposort_data = {}
    for name, feat in entrypoint_features.items():
        feat_required_dependencies = []
        dependencies = set()
        for dependency_item in feat.dependencies:
            if not dependency_item.endswith('[optional]'):
                feat_required_dependencies.append(dependency_item)
            else:
                dependency_item = dependency_item[0:len(dependency_item) - len('[optional]')]
            dependencies.add(dependency_item)

        toposort_data[name] = dependencies
        required_dependencies[name] = feat_required_dependencies
    return required_dependencies, toposort_data


def _check_missing_dependencies(entrypoint_features, required_dependencies):
    """
    Check missing required dependencies
    """
    for name, feat_required_dependencies in required_dependencies.items():
        for required_dependency in feat_required_dependencies:
            if required_dependency not in entrypoint_features.keys():
                raise ValueError("A required dependency is missing for " +
                                 name + " feature (" + required_dependency + ")")


def reset_available_features():
    """
    Reset available features to default list.
    """
    global _available_features  # pylint:disable=global-statement
    _available_features = list(_default_available_features)


def append_available_feature(feature):
    """
    Append a feature to available features list.
    """
    global _available_features  # pylint:disable=global-statement
    _available_features.append(feature)


def bootstrap_register_features():
    """
    Register all features in order.
    :return:
    """
    config.load()
    features.clear()
    for feature in get_sorted_features():
        features.register(feature)
    config.clear()


def bootstrap_features_configuration():
    """
    Preconfigure features with default bootstrap configuration.
    :return:
    """
    try:
        filenames, extensions = config.filenames, config.extensions

        config.filenames, config.extensions = (), ()

        enabled_features = [f for f in features.all() if not f.disabled]
        for feature in enabled_features:
            feature.configure(bootstrap=True)

    finally:
        config.filenames, config.extensions = filenames, extensions


def load_bootstrap_config():
    """
    Load bootstrap configuration.
    """
    bootstrap_features_configuration()
    config.load(config.data)
    migrations.migrate(config.data)
