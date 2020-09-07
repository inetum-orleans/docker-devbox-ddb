Certs
===

For some project, we needed to have SSL activated for HTTPS access of our projects. So, SSL certificates became a 
project dependency. 

The issue was that in local environments, sometimes we cannot open port 80 to the world and get a true Let's Encrypt 
certificate or don't want to use the native *traefik* certificate management.

One solution we found is to manage certificates using [CFSSL](https://github.com/cloudflare/cfssl) to generate
and manage a true certificate generation locally. This feature currently handle only CFSSL certificate generation and 
management.

Feature configuration
--- 

- `disabled`: Definition of the status of the feature. If set to True, this feature will not be triggered.
    - type: boolean
    - default: False
- `cfssl.append_ca_certificate`: if the CA certificate must be happened to the others. This is important if you have one.
    - type: boolean
    - default: `true`
- `cfssl.server.host`: the CFSSL host.
    - type: string
    - default: `localhost`
- `cfssl.server.port`: the CFSSL port on the designated host.
    - type: integer
    - default: 7780
- `cfssl.server.ssl`: if CFSSL only work on with SSL activated.
    - type: boolean
    - default: `false`
- `cfssl.server.vertify_cert`: if CFSSL certificated needs to be verified.
    - type: boolean
    - default: `true`
- `cfssl.verify_checksum`: if the certificate checksum must be checked.
    - type: boolean
    - default: `true`
- `cfssl.writer.filenames.certificate`: the template name of generated certificates.
    - type: string
    - default: `%s.crt`
- `cfssl.writer.filenames.certificate_der`: the template name of DER encoded generated certificates.
    - type: string
    - default: `%s.crt.der`
- `cfssl.writer.filenames.certificate_request`: the template name of CSR certificates.
    - type: string
    - default: `%s.csr`
- `cfssl.writer.filenames.certificate_request_der`: the template name of CSR DER encoded certificates.
    - type: string
    - default: `%s.csr.der`
- `cfssl.writer.filenames.private_key`: the template name of private key generated.
    - type: string
    - default: `%s.key`
- `destination`: the destination folder of generated certificates.
    - type: string
    - default: `.certs`
- `signer_destinations`: Additional destinations for signer certificates.
    - type: List of string
    - default: `[]`
- `type`: Definition of the type of certificate management. Currently, only `cfssl` is handled, others will not trigger.
          this feature actions.
    - type: string
    - default: `cfssl`

!!! example "Configuration"
    ```yaml
    certs:
      cfssl:
        append_ca_certificate: true
        server:
          host: localhost
          port: 7780
          ssl: false
          verify_cert: true
        verify_checksum: true
        writer:
          filenames:
            certificate: '%s.crt'
            certificate_der: '%s.crt.der'
            certificate_request: '%s.csr'
            certificate_request_der: '%s.csr.der'
            private_key: '%s.key'
      destination: .certs
      disabled: false
      type: cfssl
    ```

Certificate generation
---

When running `ddb configure` command, this action will be triggered. Based on the configuration, the right certificate
manager will be used to generate the appropriate certificate in the `certs.destination` folder if it does not already
exist.

At the end, it will trigger a `certs.generated` and `certs.available` event which can be used by other features to use 
those generated certificates.

For instance, the [traefik](./traefik.md#certificates-installation-feature) is listening for the `certs.available` event
in order to update the configuration in order to use them for HTTPS.

Certificate removal
---

When running `ddb configure` command, this action will be triggered. Based on the configuration, if certificates 
was generated before and the `certs.type` is switch to something else than `cfssl`, those certificates will be deleted.

At the end, it will trigger a `certs.removed` event which can be used by other features to update themselves.

For instance, the [traefik](./traefik.md#certificates-installation-feature) is listening for the `certs.removed` event
in order to update the configuration in order to remove them. 