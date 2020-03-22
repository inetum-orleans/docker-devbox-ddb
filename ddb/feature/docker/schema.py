# -*- coding: utf-8 -*-
import os

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


class ComposeSchema(Schema):
    """
    Docker compose schema
    """
    bin = fields.String(required=True, default="docker-compose" if os.name != "nt" else "docker-compose.exe")
    args = fields.List(fields.String(), default=[])


class ReverseProxySchema(Schema):
    """
    Reverse proxy schema.
    """
    type = fields.String(required=True, default="traefik")
    network_id = fields.String(required=True, default="reverse-proxy")
    network_names = fields.Dict(required=True, default={"reverse-proxy": "reverse-proxy"})


class DockerSchema(FeatureSchema):
    """
    Docker schema.
    """
    user = fields.Nested(UserSchema(), required=True, default=UserSchema())
    ip = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    restart_policy = fields.String(required=True, default="no")
    port_prefix = fields.Integer(required=False)  # default is set in feature _configure_defaults
    registry = fields.Nested(RegistrySchema(), required=False)
    interface = fields.String(required=True, default="docker0")
    directory = fields.String(required=True, default=".docker")
    compose = fields.Nested(ComposeSchema(), required=True, default=ComposeSchema())
    cache_from_image = fields.Boolean(required=True, default=False)
    reverse_proxy = fields.Nested(ReverseProxySchema(), required=True, default=ReverseProxySchema())
