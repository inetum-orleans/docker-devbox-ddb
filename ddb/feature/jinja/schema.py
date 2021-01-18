# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class JinjaSchema(FeatureSchema):
    """
    Jinja schema.
    """
    suffixes = fields.List(fields.String(), default=[".jinja"])
    extensions = fields.List(fields.String(), default=[".*", ""])
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String())
    options = fields.Dict(fields.String(required=True), fields.Field(required=True), allow_none=True, default=None)
