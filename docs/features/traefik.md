Traefik
===

One component which we often use on our dev environment is [Traefik](https://containo.us/traefik/) as reverse proxy.
It allows us to run dockerized projects and access them in our browser using `project.test` as DNS for example.

The feature does not install traefik or handle the configuration of your host to map the DNS entry to the IP,
but it handles the generation of traefik configuration file for your project if there is certificates for HTTPS 
access.

!!! summary "Feature configuration (prefixed with `traefik.`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
        | `extra_services` | dict[string, **ExtraService**]<br>`[]` | A dict of ExtraService configuration. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `certs_directory` | string<br>`${core.path.home}/certs` | Custom certificates location. |
        | `mapped_certs_directory` | string<br>`${core.path.home}/certs` | Traefik container custom certificates location. |
        | `config_directory` | string<br>`${core.path.home}/traefik/config` | Traefik configuration directory. |
        | `ssl_config_template` | string<br>`<Jinja template>` | The Jinja template for the traefik configuration file registering CFSSL SSL certificates. This template can be a template string, or a link to a file containing the template, prefixed with `http(s)://` for web files, or `file://` for local ones. |
        | `extra_services_config_template` | string<br>`<Jinja template>` | The Jinja template for extra-services configuration file. This template can be a template string, or a link to a file containing the template, prefixed with `http(s)://` for web files, or `file://` for local ones. |

!!! summary "ExtraService configuration (used in `traefik.extra_services`)"
    === "Simple"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `domain` | string<span style="color:red">*</span> | Domain to use for SSL certificate generation. |
        | `url` | string<span style="color:red">*</span> | URL to access the service to proxy from traefik container. |
        | `https` | boolean | Use http and/or https to expose the service. If `None`, it is exposed with both http and https. |
        | `redirect_to_https` | boolean<br>`${docker.reverse_proxy.redirect_to_https}` | If `https` is `None` and `redirect_to_https` is `True`, requesting the http url of the service will reply with a temporary redirect to https. |

    === "Advanced"
        | Property | Type | Description |
        | :---------: | :----: | :----------- |
        | `path_prefix` | string | The traefik prefix path. You should customize it only if you have to support sub folder on the domain. |
        | `redirect_to_path_prefix` | boolean | The traefik prefix path. You should customize it only if you have to support sub folder on the domain. |
        | `rule` | string<br>``Host(`{{_local.domain}}`)`` | Custom certificates location. |

Include a service running outside of docker compose
---
If you need to register an external service into your docker network, you should define an `external_service` entry.

It can be used when a service is running outside the docker network, like on another Machine or on the developer host.

Declared extra services make them join the docker network so it behaves like a docker compose service and brings all 
traefik reverse-proxy features (SSL support, domain name, ...).

Jinja templating is available for `url`, `domain` and `rule` fields, with the usual configuration as data context, 
and additional `_local` dict containing the extra_service entry configuration.

!!! example "Bring back a dockerized service inside your IDE"

    Running the server component inside the developer editor may more convenient in some cases.
    
    If the application is running on port 8080 right on the host, you can write this kind of configuration:
    
    ```yaml
    traefik:
      extra_services:
        api:
          domain: api.{{core.domain.sub}}.{{core.domain.ext}}
          url: http://{{docker.debug.host}}:8080
    ```
    
    It will expose the server component throw the traefik docker network, with the domain name and HTTPS support.

Custom certificates feature
---

If your project have certificates for SSL access, Traefik needs a bit a configuration in order to use them.

This is done on `ddb configure` command. For instance, if your have set `docker.reverse-proxy.certresolver` with `null` 
value in your `docker-compose.yml.jsonnet` (check feature [jsonnet](./jsonnet.md) for more details), 
it will create a label `ddb.emit.certs:generate: <domain>`.

This label emit a `certs:generate` for given `domain`, and it is processed by [certs](./certs.md) feature to generate a 
custom SSL certificate.

Then, `certs:available` event is triggered and handled by traefik feature to install this certificate in the 
traefik configuration for given `domain`.

For some reason, you might want to remove HTTPS on your project and move back to HTTP. 

This is done on `ddb configure` command.
If you define `docker.reverse-proxy.certresolver` value to 'letsencrypt', or set `traefik.https` to `False`, it is 
detected that you removed it. 

The `certs:remove` event is then triggered and handled by [certs](./certs.md) feature to remove it.

Then, `certs:removed` event is triggered and handler by traefik feature to uninstall this certificate from traefik 
configuration, so there's no more certificate defined for the given domain.
