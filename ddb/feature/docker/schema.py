# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class UserSchema(Schema):
    """
    Docker user schema.
    """
    uid = fields.Integer(required=True, default=None)  # default is set in feature _auto_configure
    gid = fields.Integer(required=True, default=None)  # default is set in feature _auto_configure


class CopyToBuildContextSchema(Schema):
    """
    Copy to build context schema.
    """
    source = fields.String(required=True)
    destination = fields.String(required=True, default=".")
    filename = fields.String(required=False)
    service = fields.String(required=False)


class DockerSchema(FeatureSchema):
    """
    Docker schema.
    """
    user = fields.Nested(UserSchema(), required=True, default=UserSchema())
    ip = fields.String(required=True, default=None)  # default is set in feature _auto_configure
    interface = fields.String(required=True, default="docker0")
    directory = fields.String(required=True, default=".docker")
    copy_to_build_context = fields.List(fields.Nested(CopyToBuildContextSchema(), default=None))
