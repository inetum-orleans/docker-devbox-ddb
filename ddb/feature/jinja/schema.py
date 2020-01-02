# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class JinjaSchema(FeatureSchema):
    """
    Symlinks schema.
    """
    includes = fields.List(fields.String(), default=["**/*.jinja*"])
    suffixes = fields.List(fields.String(), default=[".jinja"])
    excludes = fields.List(fields.String(), default=["**/_*"])
