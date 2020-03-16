# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class JinjaSchema(FeatureSchema):
    """
    Symlinks schema.
    """
    suffixes = fields.List(fields.String(), default=[".jinja"])
    extensions = fields.String(default="{.*,}")
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String(), default=["**/_*", "**/node_modules", "**/vendor"])
