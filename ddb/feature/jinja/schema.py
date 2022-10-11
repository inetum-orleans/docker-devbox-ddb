# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class JinjaSchema(FeatureSchema):
    """
    Jinja schema.
    """
    suffixes = fields.List(fields.String(), dump_default=[".jinja"])
    extensions = fields.List(fields.String(), dump_default=[".*", ""])
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String(), dump_default=["**/_*"])
    options = fields.Dict(fields.String(required=True), fields.Field(required=True), allow_none=True, dump_default=None)
