from marshmallow import fields

from ddb.feature.schema import FeatureSchema


class SelfUpdateSchema(FeatureSchema):
    """
    SelfUpdate schema.
    """
    github_repository = fields.String(required=True, default="gfi-centre-ouest/docker-devbox-ddb")
