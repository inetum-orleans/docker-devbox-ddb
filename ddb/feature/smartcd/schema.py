# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class SmartcdSchema(FeatureSchema):
    """
    Permissions Schema
    """
    aliases = fields.Dict(required=False, default={})
