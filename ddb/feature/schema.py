# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class DisableableSchema(Schema):
    """
    Base feature schema.
    """
    disabled = fields.Bool(default=False)


class FeatureSchema(DisableableSchema):
    """
    Base feature schema.
    """
