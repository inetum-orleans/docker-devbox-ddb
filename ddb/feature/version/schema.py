# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class VersionSchema(FeatureSchema):
    """
    Git schema.
    """
    branch = fields.String(allow_none=True)  # default is set in feature _configure_defaults
    tag = fields.String(allow_none=True)  # default is set in feature _configure_defaults
    version = fields.String(allow_none=True)  # default is set in feature _configure_defaults
    hash = fields.String(allow_none=True)  # default is set in feature _configure_defaults
    short_hash = fields.String(allow_none=True)  # default is set in feature _configure_defaults
