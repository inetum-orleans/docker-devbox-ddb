# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class SuffixesSchema(Schema):
    """
    Suffixes schema
    """
    available = fields.List(fields.String())  # default is provided by core feature (core.env.available)
    current = fields.String()  # default is the last value of available_suffixes


class SymlinksSchema(FeatureSchema):
    """
    Symlinks schema.
    """
    targets = fields.List(fields.String(), default=[])
    suffixes = fields.Nested(SuffixesSchema(), required=True, default=SuffixesSchema())
