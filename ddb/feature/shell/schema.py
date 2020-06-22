# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class PathSchema(Schema):
    """
    Shell schema.
    """
    directories = fields.List(fields.String(), required=False, default=[".bin", "bin"])
    prepend = fields.Boolean(default=True)


class ShellSchema(FeatureSchema):
    """
    Shell schema.
    """
    shell = fields.String(required=True)
    path = fields.Nested(PathSchema, required=True, default=PathSchema())
    envignore = fields.List(fields.String(), required=False, default=[
        "PYENV_*", "_", "PS1", "PS2", "PS3", "PS4"
    ])
    aliases = fields.Dict(required=False, default={})
