# -*- coding: utf-8 -*-
import os

from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class PathSchema(Schema):
    """
    Path settings for core feature schema.
    """
    project_home = fields.String(default=None)  # default is set in feature _configure_defaults
    home = fields.String(default=None, allow_none=True)  # default is set in feature _configure_defaults
    ddb_home = fields.String(default=None, allow_none=True)  # default is set in feature _configure_defaults


class EnvSchema(Schema):
    """
    Env settings for core feature schema.
    """
    current = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    available = fields.List(fields.String, required=True, default=["prod", "stage", "ci", "dev"])


class DomainSchema(Schema):
    """
    Domain settings for core feature schema.
    """
    sub = fields.String(required=True, default=None)  # default is set in feature _configure_defaults
    ext = fields.String(required=True, default="test")
    value = fields.String(required=True, default=None)  # default is set in feature _configure_defaults


class ProjectSchema(Schema):
    """
    Env settings for core feature schema.
    """
    name = fields.String(required=True, default=None)  # default is set in feature _configure_defaults


class ProcessSchema(Schema):
    """
    Process settings for core feature schema.
    """
    bin = fields.String(required=False, allow_none=True, default=None)
    prepend = fields.Raw(required=False, allow_none=True, default=None)  # List[str] or str splitted with shlex
    append = fields.Raw(required=False, allow_none=True, default=None)  # List[str] or str splitted with shlex


class ConfigurationSchema(Schema):
    """
    Process settings for core feature schema.
    """
    extra = fields.List(fields.String(), required=False)


class CoreFeatureSchema(FeatureSchema):
    """
    Core feature schema.
    """
    env = fields.Nested(EnvSchema(), default=EnvSchema())
    domain = fields.Nested(DomainSchema(), default=DomainSchema())
    project = fields.Nested(ProjectSchema(), default=ProjectSchema())
    os = fields.String(required=True, default=os.name)
    path = fields.Nested(PathSchema(), default=PathSchema())
    process = fields.Dict(fields.String(), fields.Nested(ProcessSchema()), default={})  # Process binary mappings
    configuration = fields.Nested(ConfigurationSchema(), default=ConfigurationSchema())
    github_repository = fields.String(required=True, default="inetum-orleans/docker-devbox-ddb")
    required_version = fields.String(required=False, allow_none=True, default=None)
