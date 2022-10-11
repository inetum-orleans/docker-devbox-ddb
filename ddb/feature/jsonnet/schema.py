# -*- coding: utf-8 -*-

from marshmallow import fields, Schema
from marshmallow_union import Union

from ddb.feature.schema import FeatureSchema, DisableableSchema


class RegistrySchema(Schema):
    """
    Registry schema
    """
    name = fields.String(required=False, allow_none=True, dump_default=None)
    repository = fields.String(required=False, allow_none=True, dump_default=None)


class BuildContextSchema(Schema):
    """
    Build context schema
    """
    base_directory = fields.String(required=True, dump_default=".docker")
    use_project_home = fields.Boolean(required=False, dump_default=False)


class BuildSchema(DisableableSchema):
    """
    Build schema
    """
    cache_from_image = fields.Boolean(required=True, dump_default=False)
    context = fields.Nested(BuildContextSchema(), dump_default=BuildContextSchema())
    image_tag = fields.String(required=False, allow_none=True,
                              dump_default=None)  # default is set in feature _configure_defaults
    image_tag_from = Union(fields=[fields.Boolean(), fields.String()],
                           required=False, allow_none=True, dump_default=False)


class BinarySchema(DisableableSchema):
    """
    Binary schema
    """
    global_ = fields.Boolean(data_key='global', attribute='global', required=False, allow_none=True, dump_default=None)


class VirtualhostSchema(DisableableSchema):  # Replacement for docker.reverse-proxy schema
    """
    VirtualHost schema
    """
    type = fields.String(required=True, dump_default="traefik")
    network_id = fields.String(required=True, dump_default="reverse-proxy")
    certresolver = fields.String(required=False, allow_none=True, dump_default=None)
    https = fields.Boolean(required=True, dump_default=True)
    redirect_to_https = fields.Boolean(required=False, allow_none=True, dump_default=None)
    redirect_to_path_prefix = fields.Boolean(required=False, allow_none=True, dump_default=None)


class XDebugSchema(DisableableSchema):
    """
    XDebug schema
    """
    host = fields.String(required=True, allow_none=True,
                         dump_default=None)  # default is set in feature _configure_defaults
    mode = fields.String(required=False, dump_default="debug")
    version = fields.String(required=False, allow_none=True, dump_default=None)
    session = fields.String(required=False, allow_none=True,
                            dump_default=None)  # default is set in feature _configure_defaults


class ServiceSchema(DisableableSchema):
    """
    Service schema
    """
    init = fields.Boolean(required=False, dump_default=True)
    restart = fields.String(required=False, allow_none=True, dump_default=None)


class ExposeSchema(DisableableSchema):
    """
    Expose schema
    """
    port_prefix = fields.Integer(required=False)  # default is set in feature _configure_defaults


class MountSchema(DisableableSchema):
    """
    Mount schema
    """
    directory = fields.String(required=False, allow_none=True, dump_default=None)
    directories = fields.Dict(required=False, allow_none=True, dump_default=None,
                              keys=fields.String(), values=fields.String())


class UserSchema(DisableableSchema):
    """
    User schema
    """
    uid = fields.Integer(required=True, dump_default=None)  # default is set in feature _configure_defaults
    gid = fields.Integer(required=True, dump_default=None)  # default is set in feature _configure_defaults
    name = fields.String(required=False, allow_none=True,
                         dump_default=None)  # default is set in feature _configure_defaults
    group = fields.String(required=False, allow_none=True,
                          dump_default=None)  # default is set in feature _configure_defaults
    name_to_uid = fields.Dict(required=True, dump_default={})
    group_to_gid = fields.Dict(required=True, dump_default={})


class ComposeSchema(Schema):
    """
    Docker compose schema
    """
    project_name = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults
    network_name = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults
    version = fields.String(required=True, dump_default="3.7")
    excluded_services = fields.List(fields.String(), required=False, allow_none=True, dump_default=[])
    included_services = fields.List(fields.String(), required=False, allow_none=True, dump_default=None)


class NetworksSchema(Schema):
    """
    Networks schema.
    """
    names = fields.Dict(required=True, dump_default={})


class DockerSchema(Schema):
    """
    Docker schema
    """
    compose = fields.Nested(ComposeSchema(), dump_default=ComposeSchema())
    networks = fields.Nested(NetworksSchema(), dump_default=NetworksSchema())
    build = fields.Nested(BuildSchema(), dump_default=BuildSchema())
    service = fields.Nested(ServiceSchema(), dump_default=ServiceSchema())
    expose = fields.Nested(ExposeSchema(), dump_default=ExposeSchema())
    mount = fields.Nested(MountSchema(), dump_default=MountSchema())
    registry = fields.Nested(RegistrySchema(), dump_default=RegistrySchema())
    user = fields.Nested(UserSchema(), dump_default=UserSchema())
    binary = fields.Nested(BinarySchema(), dump_default=BinarySchema())
    virtualhost = fields.Nested(VirtualhostSchema(), dump_default=VirtualhostSchema())
    xdebug = fields.Nested(XDebugSchema(), dump_default=XDebugSchema())


class JsonnetSchema(FeatureSchema):
    """
    Jsonnet schema.
    """
    suffixes = fields.List(fields.String(), dump_default=[".jsonnet"])
    extensions = fields.List(fields.String(), dump_default=[".*", ""])
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String())
    docker = fields.Nested(DockerSchema(), dump_default=DockerSchema())
