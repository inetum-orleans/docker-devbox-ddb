# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class FileSchema(FeatureSchema):
    """
    File schema.
    """
    suffixes = fields.List(fields.String())
    extensions = fields.List(fields.String())
    includes = fields.List(fields.String())
    excludes = fields.List(fields.String(), default=["**/_*", "**/.git", "**/node_modules", "**/vendor"])
