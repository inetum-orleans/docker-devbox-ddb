# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class GitSchema(FeatureSchema):
    """
    Git schema.
    """
    auto_umask = fields.Bool(default=True)
