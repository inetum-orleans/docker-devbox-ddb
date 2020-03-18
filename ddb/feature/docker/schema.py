# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class UserSchema(Schema):
    """
    Docker user schema.
    """
    uid = fields.Integer(required=True, default=None)  # default is set in feature _configure_defaults
    gid = fields.Integer(required=True, default=None)  # default is set in feature _configure_defaults


class RegistrySchema(Schema):
    """
    Docker registry schema
    """
    name = fields.String(required=False)
    repository = fields.String(required=False)


class DockerSchema(FeatureSchema):
    """
    Docker schema.
    """
    user = fields.Nested(UserSchema(), required=True, default=UserSchema())
    ip = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    restart_policy = fields.String(required=True, default="no")
    port_prefix = fields.Integer(required=False)
    registry = fields.Nested(RegistrySchema(), required=False)
    interface = fields.String(required=True, default="docker0")
