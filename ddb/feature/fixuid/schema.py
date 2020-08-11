# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class FixuidSchema(FeatureSchema):
    """
    Certs feature schema.
    """
    url = fields.String(required=True, default="https://github.com/boxboat/fixuid/releases/download/"
                                               "v0.5/fixuid-0.5-linux-amd64.tar.gz")
