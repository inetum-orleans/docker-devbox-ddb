# -*- coding: utf-8 -*-

from marshmallow import fields, Schema
from marshmallow_union import Union

from ddb.feature.schema import FeatureSchema, DisableableSchema


class RegistrySchema(Schema):
    """
    Registry schema
    """
    name = fields.String(required=False, allow_none=True, default=None)
    repository = fields.String(required=False, allow_none=True, default=None)


class BuildContextSchema(Schema):
    """
    Build context schema
    """
    base_directory = fields.String(required=True, default=".docker")
    use_project_home = fields.Boolean(required=False, default=False)


class BuildSchema(DisableableSchema):
    """
    Build schema
    """
    cache_from_image = fields.Boolean(required=True, default=False)
    context = fields.Nested(BuildContextSchema(), default=BuildContextSchema())
    image_tag = fields.String(required=False, allow_none=True,
                              default=None)  # default is set in feature _configure_defaults
    image_tag_from = Union(fields=[fields.Boolean(), fields.String()],
                           required=False, allow_none=True, default=False)


class BinarySchema(DisableableSchema):
    """
    Binary schema
    """
    global_ = fields.Boolean(data_key='global', attribute='global', required=False, allow_none=True, default=None)


class VirtualhostSchema(DisableableSchema):  # Replacement for docker.reverse-proxy schema
    """
    VirtualHost schema
    """
    type = fields.String(required=True, default="traefik")
    network_id = fields.String(required=True, default="reverse-proxy")
    certresolver = fields.String(required=False, allow_none=True, default=None)
    https = fields.Boolean(required=True, default=True)
    redirect_to_https = fields.Boolean(required=False, allow_none=True, default=None)
    redirect_to_path_prefix = fields.Boolean(required=False, allow_none=True, default=None)


class XDebugSchema(DisableableSchema):
    """
    XDebug schema
    """
    host = fields.String(required=True, allow_none=True, default=None)  # default is set in feature _configure_defaults
    mode = fields.String(required=False, default="debug")
    version = fields.String(required=False, allow_none=True, default=None)
    session = fields.String(required=False, allow_none=True,
                            default=None)  # default is set in feature _configure_defaults


class ServiceSchema(DisableableSchema):
    """
    Service schema
    """
    init = fields.Boolean(required=False, default=True)
    restart = fields.String(required=False, allow_none=True, default=None)


class ExposeSchema(DisableableSchema):
    """
    Expose schema
    """
    port_prefix = fields.Integer(required=False)  # default is set in feature _configure_defaults


class MountSchema(DisableableSchema):
    """
    Mount schema
    """
    directory = fields.String(required=False, allow_none=True, default=None)
    directories = fields.Dict(required=False, allow_none=True, default=None,
                              keys=fields.String(), values=fields.String())


class UserSchema(DisableableSchema):
    """
    User schema
    """
    uid = fields.Integer(required=True, default=None)  # default is set in feature _configure_defaults
    gid = fields.Integer(required=True, default=None)  # default is set in feature _configure_defaults
    name = fields.String(required=False, allow_none=True, default=None)  # default is set in feature _configure_defaults
    group = fields.String(required=False, allow_none=True,
                          default=None)  # default is set in feature _configure_defaults
    name_to_uid = fields.Dict(required=True, default={})
    group_to_gid = fields.Dict(required=True, default={})


class ComposeSchema(Schema):
    """
    Docker compose schema
    """
    project_name = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    network_name = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    version = fields.String(required=True, default="3.7")
    excluded_services = fields.List(fields.String(), required=False, allow_none=True, default=[])
    included_services = fields.List(fields.String(), required=False, allow_none=True, default=None)


class NetworksSchema(Schema):
    """
    Networks schema.
    """
    names = fields.Dict(required=True, default={})


class DockerSchema(Schema):
    """
    Docker schema
    """
    compose = fields.Nested(ComposeSchema(), default=ComposeSchema())
    networks = fields.Nested(NetworksSchema(), default=NetworksSchema())
    build = fields.Nested(BuildSchema(), default=BuildSchema())
    service = fields.Nested(ServiceSchema(), default=ServiceSchema())
    expose = fields.Nested(ExposeSchema(), default=ExposeSchema())
    mount = fields.Nested(MountSchema(), default=MountSchema())
    registry = fields.Nested(RegistrySchema(), default=RegistrySchema())
    user = fields.Nested(UserSchema(), default=UserSchema())
    binary = fields.Nested(BinarySchema(), default=BinarySchema())
    virtualhost = fields.Nested(VirtualhostSchema(), default=VirtualhostSchema())
    xdebug = fields.Nested(XDebugSchema(), default=XDebugSchema())


class JsonnetSchema(FeatureSchema):
    """
    Jsonnet schema.
    """
    suffixes = fields.List(fields.String(), default=[".jsonnet"])
    extensions = fields.List(fields.String(), default=[".*", ""])
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String())
    docker = fields.Nested(DockerSchema(), default=DockerSchema())
