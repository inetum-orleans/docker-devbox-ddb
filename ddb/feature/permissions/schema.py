# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class PermissionsSchema(FeatureSchema):
    """
    Permissions Schema
    """
    specs = fields.Dict(fields.String(required=True), fields.String(required=True), allow_none=True, default=None)
