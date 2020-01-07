# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

from ddb.feature.schema import FeatureSchema


class CookiecutterOptions(Schema):
    """
    Cookiecutter options
    """
    no_input = fields.Boolean(allow_none=True, default=None)
    replay = fields.Boolean(allow_none=True, default=None)
    overwrite_if_exists = fields.Boolean(allow_none=True, default=None)
    config_file = fields.String(allow_none=True, default=None)
    default_config = fields.Raw(allow_none=True, default=None)


class TemplateSchema(CookiecutterOptions):
    """
    Template schema
    """
    template = fields.String(required=True)
    output_dir = fields.String(allow_none=True, default=None)
    checkout = fields.String(allow_none=True, default=None)
    extra_context = fields.Dict(allow_none=True, default=None)
    password = fields.String(allow_none=True, default=None)
    version = fields.String(allow_none=True, default=None)


class CookiecutterFeatureSchema(FeatureSchema, CookiecutterOptions):
    """
    Cookiecutter feature schema.
    """
    templates = fields.List(fields.Nested(TemplateSchema()))
    cookiecutters_dir = fields.String(allow_none=True, default=".cookiecutter/templates")
    replay_dir = fields.String(allow_none=True, default=".cookiecutter/replay")
    default_context = fields.Dict(allow_none=True)
