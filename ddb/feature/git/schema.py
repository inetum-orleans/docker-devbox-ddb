# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class GitSchema(FeatureSchema):
    """
    Git schema.
    """
    fix_files_permissions = fields.Bool(default=True)
