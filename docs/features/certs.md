Certs
===

For some project, we needed to have SSL activated for HTTPS access of our projects. So, SSL certificates became a
project dependency.

The issue was that in local environments, sometimes we cannot open port 80 to the world and get a true Let's Encrypt
certificate or don't want to use the native *traefik* certificate management.

One solution we found is to manage certificates using [CFSSL](https://github.com/cloudflare/cfssl) to generate and
manage a true certificate generation locally. This feature currently handle only CFSSL certificate generation and
management.

!!! summary "Feature configuration (prefixed with `certs.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `type` | string<br>`cfssl` | Type of certificate generation. Currently, only `cfssl` is supported. |
        | `cfssl.server.host` | boolean<br>`localhost` | CFSSL host (without protocol). |
        | `cfssl.server.port` | integer<br>`7780` | CFSSL port to connect to. |
        | `cfssl.server.ssl` | integer<br>`false` | Should SSL be used to connect ? |
        | `cfssl.server.verify_cert` | integer<br>`false` | Should the CFSSL SSL certificate be verified on connect ? |
    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `cfssl.verify_checksum` | integer<br>`false` | Should the CFSSL generated certificates be verified with checksums. |
        | `cfssl.append_ca_certificate` | boolean<br>`true` | Should the signer (CA) certificate be appended to the generated certificate ? |
        | `destination` | string<br>`.certs` | Destination directory of generated certificates. |
        | `signer_destinations` | string[]<br>`[]` | Additional destinations for signer (CA) certificates. |
    === "Internal"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `cfssl.writer.filenames.certificate` | string<br>`%s.crt` | Filename template of generated PEM certificates. |
        | `cfssl.writer.filenames.certificate_der` | string<br>`%s.crt.der` | Filename template of generated DER certificates. |
        | `cfssl.writer.filenames.certificate_request` | string<br>`%s.csr` | Filename template of PEM generated certificate requests. |
        | `cfssl.writer.filenames.certificate_request_der` | string<br>`%s.csr.der` | Filename template of name of DER geberated certificate requests. |
        | `cfssl.writer.filenames.private_key` | string<br>`%s.key` | Filename template of generated PEM private key. |

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

When running `ddb configure` command, this action will be triggered. Based on the configuration, if certificates was
generated before and the `certs.type` is switch to something else than `cfssl`, those certificates will be deleted.

At the end, it will trigger a `certs.removed` event which can be used by other features to update themselves.

For instance, the [traefik](./traefik.md#certificates-installation-feature) is listening for the `certs.removed` event
in order to update the configuration in order to remove them. 