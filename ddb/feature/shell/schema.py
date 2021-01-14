# -*- coding: utf-8 -*-
import os

from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema
from ...config import config


def _get_path_default():
    _path_default = []

    if config.paths.project_home:
        _path_default.append(".bin")
        _path_default.append("bin")

    if config.paths.home:
        _path_default.append(os.path.join(config.paths.home, ".bin"))

    if config.paths.ddb_home:
        _path_default.append(os.path.join(config.paths.ddb_home, ".bin"))

    return _path_default


class PathSchema(Schema):
    """
    Shell schema.
    """
    directories = fields.List(fields.String(), required=False, default=_get_path_default)
    prepend = fields.Boolean(default=True)


class ShellSchema(FeatureSchema):
    """
    Shell schema.
    """
    shell = fields.String(required=True)
    path = fields.Nested(PathSchema, required=True, default=PathSchema())
    envignore = fields.List(fields.String(), required=False, default=[
        "PYENV_*", "_", "PS1", "PS2", "PS3", "PS4", "PWD"
    ])
    aliases = fields.Dict(required=False, default={})
    global_aliases = fields.List(fields.String(), required=False, default=[])
