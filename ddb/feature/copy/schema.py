# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class CopySpecSchema(Schema):
    """
    Copy to build context schema.
    """
    source = fields.String(required=True)
    destination = fields.String(required=True, dump_default=".")
    filename = fields.String(required=False)
    dispatch = fields.List(fields.String(), required=False)


class CopySchema(FeatureSchema):
    """
    Copy schema.
    """
    specs = fields.List(fields.Nested(CopySpecSchema(), dump_default=None))
