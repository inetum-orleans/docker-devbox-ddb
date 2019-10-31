# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class EnvSchema(Schema):
    """
    Env settings for core feature schema.
    """
    current = fields.String(required=True, default=None)  # default is set in feature _auto_configure
    available = fields.List(fields.String, required=True, default=["prod", "stage", "dev"])


class CoreFeatureSchema(FeatureSchema):
    """
    Core feature schema.
    """
    env = fields.Nested(EnvSchema(), default=EnvSchema())
