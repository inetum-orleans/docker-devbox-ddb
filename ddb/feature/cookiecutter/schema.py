# -*- coding: utf-8 -*-
import os
import tempfile

from marshmallow import Schema, fields

from ddb.feature.schema import FeatureSchema


class CookiecutterOptions(Schema):
    """
    Cookiecutter options
    """
    no_input = fields.Boolean(allow_none=True, dump_default=None)
    replay = fields.Boolean(allow_none=True, dump_default=False)
    overwrite_if_exists = fields.Boolean(allow_none=True, dump_default=True)
    config_file = fields.String(allow_none=True, dump_default=None)
    default_config = fields.Raw(allow_none=True, dump_default=None)


class TemplateSchema(CookiecutterOptions):
    """
    Template schema
    """
    template = fields.String(required=True)
    output_dir = fields.String(allow_none=True, dump_default=None)
    checkout = fields.String(allow_none=True, dump_default=None)
    extra_context = fields.Dict(allow_none=True, dump_default=None)
    password = fields.String(allow_none=True, dump_default=None)
    version = fields.String(allow_none=True, dump_default=None)


cookiecutter_tmp_dir = os.path.join(tempfile.gettempdir(), "ddb", "cookiecutter")


class CookiecutterFeatureSchema(FeatureSchema, CookiecutterOptions):
    """
    Cookiecutter feature schema.
    """
    templates = fields.List(fields.Nested(TemplateSchema()))
    cookiecutters_dir = fields.String(allow_none=True, dump_default=os.path.join(cookiecutter_tmp_dir, "templates"))
    replay_dir = fields.String(allow_none=True, dump_default=os.path.join(cookiecutter_tmp_dir, "replay"))
    default_context = fields.Dict(allow_none=True)
