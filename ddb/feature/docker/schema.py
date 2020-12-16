# -*- coding: utf-8 -*-
from marshmallow import fields, Schema
from marshmallow_union import Union

from ddb.feature.schema import FeatureSchema


class UserSchema(Schema):
    """
    Docker user schema.
    """
    uid = fields.Integer(required=True, default=None)  # default is set in feature _configure_defaults
    gid = fields.Integer(required=True, default=None)  # default is set in feature _configure_defaults
    name = fields.String(required=False, allow_none=True, default=None)  # default is set in feature _configure_defaults
    group = fields.String(required=False, allow_none=True,
                          default=None)  # default is set in feature _configure_defaults
    name_to_uid = fields.Dict(required=True, default={})
    group_to_gid = fields.Dict(required=True, default={})


class RegistrySchema(Schema):
    """
    Docker registry schema
    """
    name = fields.String(required=False, allow_none=True, default=None)
    repository = fields.String(required=False, allow_none=True, default=None)


class ComposeSchema(Schema):
    """
    Docker compose schema
    """
    project_name = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    network_name = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    file_version = fields.String(required=True, default="3.7")
    service_init = fields.Boolean(required=False, default=True)
    service_context_root = fields.Boolean(required=False, default=False)


class ReverseProxySchema(Schema):
    """
    Reverse proxy schema.
    """
    type = fields.String(required=True, default="traefik")
    network_id = fields.String(required=True, default="reverse-proxy")
    network_names = fields.Dict(required=True, default={"reverse-proxy": "reverse-proxy"})
    certresolver = fields.String(required=False, allow_none=True, default=None)
    https = fields.Boolean(required=True, default=True)
    redirect_to_https = fields.Boolean(required=False, allow_none=True, default=None)
    redirect_to_path_prefix = fields.Boolean(required=False, allow_none=True, default=None)


class DebugSchema(Schema):
    """
    Debug schema
    """
    disabled = fields.Boolean(required=False, default=None)  # default is set in feature _configure_defaults
    host = fields.String(required=True, default=None)  # default is set in feature _configure_defaults


class JsonnetSchema(Schema):
    """
    Jsonnet schema
    """
    binary_disabled = fields.Boolean(required=False, default=False)
    virtualhost_disabled = fields.Boolean(required=False, default=False)


class DockerSchema(FeatureSchema):
    """
    Docker schema.
    """
    user = fields.Nested(UserSchema(), required=True, default=UserSchema())
    ip = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    debug = fields.Nested(DebugSchema(), default=DebugSchema())
    jsonnet = fields.Nested(JsonnetSchema(), default=JsonnetSchema())
    restart_policy = fields.String(required=False, allow_none=True,
                                   default=None)  # default is set in feature _configure_defaults
    port_prefix = fields.Integer(required=False)  # default is set in feature _configure_defaults
    registry = fields.Nested(RegistrySchema(), required=True, default=RegistrySchema())
    interface = fields.String(required=True, default="docker0")
    directory = fields.String(required=True, default=".docker")
    compose = fields.Nested(ComposeSchema(), required=True, default=ComposeSchema())
    cache_from_image = fields.Boolean(required=True, default=False)
    build_image_tag = fields.String(required=False, allow_none=True,
                                    default=None)  # default is set in feature _configure_defaults
    build_image_tag_from = Union(fields=[fields.Boolean(), fields.String()],
                                 required=False, allow_none=True, default=False)
    build_image_tag_from_version = fields.Boolean(required=False, default=False)  # This field is deprecated.
    reverse_proxy = fields.Nested(ReverseProxySchema(), required=True, default=ReverseProxySchema())
    path_mapping = fields.Dict(required=False)  # default is set in feature _configure_defaults
    disabled_services = fields.List(fields.String(), required=False, default=[])
