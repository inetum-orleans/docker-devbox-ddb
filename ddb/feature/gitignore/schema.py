# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class GitignoreSchema(FeatureSchema):
    """
    Git schema.
    """
    disabled = fields.Bool(dump_default=None)  # default is set in feature _configure_defaults
    enforce = fields.List(fields.String(), dump_default=["*ddb.local.*"])
    markers = fields.List(fields.String(),
                          dump_default=["inetum-orleans/docker-devbox", "gfi-centre-ouest/docker-devbox"])
