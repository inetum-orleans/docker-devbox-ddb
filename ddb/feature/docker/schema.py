# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class UserSchema(Schema):
    """
    User schema
    """
    uid = fields.Integer(required=True, dump_default=None)  # default is set in feature _configure_defaults
    gid = fields.Integer(required=True, dump_default=None)  # default is set in feature _configure_defaults
    name = fields.String(required=False, allow_none=True,
                         dump_default=None)  # default is set in feature _configure_defaults
    group = fields.String(required=False, allow_none=True,
                          dump_default=None)  # default is set in feature _configure_defaults


class DockerSchema(FeatureSchema):
    """
    Docker schema.
    """
    ip = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults
    interface = fields.String(required=True, dump_default="docker0")
    user = fields.Nested(UserSchema(), dump_default=UserSchema())
    path_mapping = fields.Dict(required=False)  # default is set in feature _configure_defaults
    docker_command = fields.String(required=True, dump_default='docker')
    docker_compose_command = fields.String(required=True, dump_default='docker compose')
