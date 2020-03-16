# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class PathSchema(Schema):
    """
    Shell schema.
    """
    directories = fields.List(fields.String(), required=False, default=["./bin"])
    prepend = fields.Boolean(default=True)


class ShellSchema(FeatureSchema):
    """
    Shell schema.
    """
    shell = fields.String(required=True)
    path = fields.Nested(PathSchema, required=True, default=PathSchema())
