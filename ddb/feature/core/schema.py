# -*- coding: utf-8 -*-
import os

from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class PathSchema(Schema):
    """
    Path settings for core feature schema.
    """
    project_home = fields.String(dump_default=None)  # default is set in feature _configure_defaults
    home = fields.String(dump_default=None, allow_none=True)  # default is set in feature _configure_defaults
    ddb_home = fields.String(dump_default=None, allow_none=True)  # default is set in feature _configure_defaults


class EnvSchema(Schema):
    """
    Env settings for core feature schema.
    """
    current = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults
    available = fields.List(fields.String, required=True, dump_default=["prod", "stage", "ci", "dev"])


class DomainSchema(Schema):
    """
    Domain settings for core feature schema.
    """
    sub = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults
    ext = fields.String(required=True, dump_default="test")
    value = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults


class ProjectSchema(Schema):
    """
    Env settings for core feature schema.
    """
    name = fields.String(required=True, dump_default=None)  # default is set in feature _configure_defaults


class ProcessSchema(Schema):
    """
    Process settings for core feature schema.
    """
    bin = fields.String(required=False, allow_none=True, dump_default=None)
    prepend = fields.Raw(required=False, allow_none=True, dump_default=None)  # List[str] or str splitted with shlex
    append = fields.Raw(required=False, allow_none=True, dump_default=None)  # List[str] or str splitted with shlex


class ConfigurationSchema(Schema):
    """
    Process settings for core feature schema.
    """
    extra = fields.List(fields.String(), required=False)


class CoreFeatureSchema(FeatureSchema):
    """
    Core feature schema.
    """
    env = fields.Nested(EnvSchema(), dump_default=EnvSchema())
    domain = fields.Nested(DomainSchema(), dump_default=DomainSchema())
    project = fields.Nested(ProjectSchema(), dump_default=ProjectSchema())
    os = fields.String(required=True, dump_default=os.name)
    path = fields.Nested(PathSchema(), dump_default=PathSchema())
    process = fields.Dict(fields.String(), fields.Nested(ProcessSchema()), dump_default={})  # Process binary mappings
    configuration = fields.Nested(ConfigurationSchema(), dump_default=ConfigurationSchema())
    github_repository = fields.String(required=True, dump_default="inetum-orleans/docker-devbox-ddb")
    check_updates = fields.Boolean(required=True, dump_default=True)
    required_version = fields.String(required=False, allow_none=True, dump_default=None)
    release_asset_name = fields.String(required=False, allow_none=True,
                                       dump_default=None)  # default is set in feature _configure_defaults
