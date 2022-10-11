# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class DisableableSchema(Schema):
    """
    Base feature schema.
    """
    disabled = fields.Bool(dump_default=False)


class FeatureSchema(DisableableSchema):
    """
    Base feature schema.
    """
