# -*- coding: utf-8 -*-

from marshmallow import fields, Schema

from ddb.feature.schema import FeatureSchema


class CfsslCertificateRequest(Schema):
    """
    CFSSL certificate request schema
    """
    org_name = fields.String()  # The full legal name of the organization. Do not abbreviate.
    org_unit = fields.String()  # Section of the organization.
    city = fields.String()  # The city where the organization is legally located.
    state = fields.String()  # The state or province where your organization is legally located. Can not be abbreviated.
    country = fields.String()  # The two letter ISO abbreviation for the country.


class CfsslServerSchema(Schema):
    """
    Cfssl server schema
    """
    host = fields.String(required=True, default="localhost")
    port = fields.Integer(required=True, default=7780)
    ssl = fields.Boolean(required=True, default=False)
    verify_cert = fields.Boolean(required=True, default=True)


class CfsslWriterFilenamesSchema(Schema):
    """
    CFSSL writer filenames schema
    """

    private_key = fields.String(required=True, default='%s.key')
    certificate = fields.String(required=True, default='%s.crt')
    certificate_request = fields.String(required=True, default='%s.csr')
    certificate_der = fields.String(required=True, default='%s.crt.der')
    certificate_request_der = fields.String(required=True, default='%s.csr.der')


class CfsslWriterSchema(Schema):
    """
    CFSSL writer schema
    """
    filenames = fields.Nested(CfsslWriterFilenamesSchema(), required=True, default=CfsslWriterFilenamesSchema())


class CfsslSchema(Schema):
    """
    Debug schema
    """
    server = fields.Nested(CfsslServerSchema(), required=True, default=CfsslServerSchema())
    append_ca_certificate = fields.Boolean(required=True, default=True)
    certificate_request = fields.List(fields.Nested(CfsslCertificateRequest()))
    verify_checksum = fields.Boolean(required=True, default=True)
    writer = fields.Nested(CfsslWriterSchema(), required=True, default=CfsslWriterSchema())


class CertsSchema(FeatureSchema):
    """
    Certs feature schema.
    """
    type = fields.String(required=True, default="cfssl")
    destination = fields.String(required=True, default=".certs")
    cfssl = fields.Nested(CfsslSchema(), required=False, default=CfsslSchema())
