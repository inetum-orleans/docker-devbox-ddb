# -*- coding: utf-8 -*-
from marshmallow import fields

from ddb.feature.schema import FeatureSchema

keywords = ["and", "elif", "in", "or", "break", "else", "lambda", "pass", "continue", "for",
            "load", "return", "def", "if", "not", "while"]

reserved = ["as", "finally", "nonlocal", "assert", "from", "raise", "class", "global", "try",
            "del", "import", "with", "except", "is", "yield"]


class YttSchema(FeatureSchema):
    """
    Ytt schema.
    """
    suffixes = fields.List(fields.String(), default=[".ytt"])
    includes = fields.List(fields.String())  # default is build automatically from suffixes value
    excludes = fields.List(fields.String())
    extensions = fields.List(fields.String(), default=[".yaml", ".yml", ""])
    depends_suffixes = fields.List(fields.String(), default=[".data", ".overlay"])
    args = fields.List(fields.String(), default=["--ignore-unknown-comments"])
    keywords = fields.List(fields.String(), default=keywords + reserved)
    keywords_escape_format = fields.String(default="%s_")
