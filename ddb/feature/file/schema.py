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
    excludes = fields.List(fields.String(), dump_default=[
        "**/.git",
        "**/.idea",
        "**/.yarn",
        "**/node_modules",
        "**/vendor",
        "**/target",
        "**/dist"
    ])
    include_files = fields.List(fields.String())
    exclude_files = fields.List(fields.String())
