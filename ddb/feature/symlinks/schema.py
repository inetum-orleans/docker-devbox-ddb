# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class SymlinksSchema(FeatureSchema):
    """
    Symlinks schema.
    """
    suffixes = fields.List(fields.String())  # default is build automatically from env value
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String())
