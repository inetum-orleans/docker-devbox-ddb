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
    host = fields.String(required=True, dump_default="localhost")
    port = fields.Integer(required=True, dump_default=7780)
    ssl = fields.Boolean(required=True, dump_default=False)
    verify_cert = fields.Boolean(required=True, dump_default=True)


class CfsslWriterFilenamesSchema(Schema):
    """
    CFSSL writer filenames schema
    """

    private_key = fields.String(required=True, dump_default='%s.key')
    certificate = fields.String(required=True, dump_default='%s.crt')
    certificate_request = fields.String(required=True, dump_default='%s.csr')
    certificate_der = fields.String(required=True, dump_default='%s.crt.der')
    certificate_request_der = fields.String(required=True, dump_default='%s.csr.der')


class CfsslWriterSchema(Schema):
    """
    CFSSL writer schema
    """
    filenames = fields.Nested(CfsslWriterFilenamesSchema(), required=True, dump_default=CfsslWriterFilenamesSchema())


class CfsslSchema(Schema):
    """
    Debug schema
    """
    server = fields.Nested(CfsslServerSchema(), required=True, dump_default=CfsslServerSchema())
    append_ca_certificate = fields.Boolean(required=True, dump_default=True)
    certificate_request = fields.List(fields.Nested(CfsslCertificateRequest()))
    verify_checksum = fields.Boolean(required=True, dump_default=True)
    writer = fields.Nested(CfsslWriterSchema(), required=True, dump_default=CfsslWriterSchema())


class CertsSchema(FeatureSchema):
    """
    Certs feature schema.
    """
    type = fields.String(required=True, dump_default="cfssl")
    destination = fields.String(required=True, dump_default=".certs")
    signer_destinations = fields.List(fields.String(), required=False, dump_default=[])
    cfssl = fields.Nested(CfsslSchema(), required=False, dump_default=CfsslSchema())
