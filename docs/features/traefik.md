Traefik
===

One component which we often use on our dev environment is [Traefik](https://containo.us/traefik/) as reverse proxy.
It allows us to run dockerized projects and access them in our browser using `project.test` as DNS for example.

The feature does not install traefik or handle the configuration of your host to map the DNS entry to the IP,
but it handles the generation of traefik configuration file for your project if there is certificates for HTTPS 
access.

Feature configuration
---

- `disabled`: Definition of the status of the feature. If set to True, traefik feature will not be triggered.
    - type: boolean
    - default: False
- `certs_directory`: The directory in which all certs are stored
    - type: string
    - default: $HOME/.docker-devbox/certs (for Linux based systems)
- `config_directory`: The traefik configuration directory
    - type: string
    - default: $HOME/.docker-devbox/traefik/config (for Linux based systems)
- `mapped_certs_directory`: The directory in which certificates are generated (public and private key)
    - type: string
    - default: /cert
- `ssl_config_template`: The template for the traefik configuration file 
    - type: string
    - default: /cert

!!! example "Configuration"
    ```yaml
    traefik:
      certs_directory: /home/vagrant/.docker-devbox/certs
      config_directory: /home/vagrant/.docker-devbox/traefik/config
      disabled: false
      mapped_certs_directory: /certs
      ssl_config_template: "# This configuration file has been automatically generated\
        \ by ddb\n[[tls.certificates]]\n  certFile = \"%s\"\n  keyFile = \"%s\"\n"
    ```
    
Certificates Installation Feature
---

If your project have certificates for SSL access, Traefik needs a bit a configuration in order to use them.

This is done on `ddb configure` command. For instance, if your have defined a certresolver with `null` value in your 
docker-compose.yml.jsonnet (check feature [jsonnet](./jsonnet.md) for more details), 
it will create a label `ddb.emit.certs:generate: <the vhost>`. 
It will then be processed by the [certs](./certs.md) feature and will generate a SSL certificate.

Then, the `certs:available` event will be triggered, which is handled by the traefik feature.

When triggered, it will generate the right configuration file in order to tell Traefik that there is a certificate 
defined for the given domain.
    
Certificates Uninstallation Feature
---

For some reason, you might want to remove HTTPS on your project and move back to HTTP. 

This is done on `ddb configure` command. 
If you have previously defined a certresolver to null, it will be detected that you removed it. 
The `certs:removed` event will be triggered, which is handled by the traefik feature.

When triggered, it will remove the configuration file and both public and private key in order to tell Traefik 
that there is no more certificate defined for the given domain.
