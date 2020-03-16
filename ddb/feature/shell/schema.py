# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class ShellSchema(FeatureSchema):
    """
    Shell schema.
    """
    shell = fields.String(required=True)
    path_additions = fields.List(fields.String(), default=["./bin"])
