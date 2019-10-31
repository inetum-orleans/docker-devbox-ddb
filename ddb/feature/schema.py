# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class FeatureSchema(Schema):
    """
    Base feature schema.
    """
    disabled = fields.Bool(default=False)
