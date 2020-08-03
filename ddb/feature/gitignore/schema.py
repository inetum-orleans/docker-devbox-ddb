# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class GitignoreSchema(FeatureSchema):
    """
    Git schema.
    """
    enforce = fields.List(fields.String(), default=["*ddb.local.*"])
