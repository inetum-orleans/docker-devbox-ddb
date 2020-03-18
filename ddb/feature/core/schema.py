# -*- coding: utf-8 -*-
from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


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


class ProjectSchema(Schema):
    """
    Env settings for core feature schema.
    """
    name = fields.String(required=True, default=None)  # default is set in feature _configure_defaults


class CoreFeatureSchema(FeatureSchema):
    """
    Core feature schema.
    """
    env = fields.Nested(EnvSchema(), default=EnvSchema())
    domain = fields.Nested(DomainSchema(), default=DomainSchema())
    project = fields.Nested(ProjectSchema(), default=ProjectSchema())
