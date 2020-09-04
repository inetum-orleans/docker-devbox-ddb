History
=======

1.0.4 (2020-09-04)
------------------

- Shell: Fix binary shims when `-h`/`--help` is given as argument.
- Core: Add the `info` command which output compacted information about docker containers such as environment 
  variables, virtual host, exposed ports and binaries.
- Jsonnet: Fix `cache_from` value for docker services to match the `image` one 
- Fixuid: Enhance fixuid configuration when image has no entrypoint defined.
- Config: Add support for `ddb.yml` configuration watch. If a project configuration file changes, configuration is 
reloaded and command is runned again to update all generated files. It currently doesn't watch configuration files 
from ~/.docker-devbox nor ~/.docker-devbox/ddb directories as it's based on `file` feature events.


1.0.3 (2020-09-01)
------------------

- Certs: Fix inversion between certificate and key for `certs:generated` and `certs:available` events.


1.0.2 (2020-08-28)
------------------

- Core: Fix `[Errno 11] Resource temporarily unavailable` error when running more than one instance of ddb.
- Aliases: Fix global aliases for projects lying inside docker devbox home directory (traefik, portainer, cfssl).

1.0.1 (2020-08-25)
------------------

- Docker: Limit `port_prefix` to  `655` instead of `1000` to avoid *invalid port specification* error.


1.0.0 (2020-08-25)
------------------

- Binaries: Fix docker binary workdir value
- Shell: Add `global_aliases` configuration option to generate aliases inside global docker devbox home.


1.0.0-beta9 (2020-08-20)
------------------------

- File: Emit delete events before found events.
- Core: Set working directory to project home.
- Fixuid: Upgrade fixuid to v0.5.


1.0.0-beta8 (2020-08-10)
------------------------

- Binary: Add exe option to use docker-compose exec instead of run
- Gitignore: Add enforce option to force addition of file to gitignore
- Certs: Add `certs.cfssl.append_ca_certificate` and `certs.cfssl.verify_checksum` options support
- Core: Add release check on --version
- Core: Fix crash when github quota has exceeded on release check

1.0.0-beta7 (2020-07-25)
------------------------

- Add MacOS support (no binary package available though)
- Shell: Add zsh support
- Jsonnet: Fix an issue when reverse proxy is not defined to traefik.
- Docs: Add way more docs

1.0.0-beta6 (2020-07-03)
------------------------

- Windows Shell: Fix alias generation
- Jsonnet: Add `redirect_to_https` to ddb.VirtualHost in order to redirect http requests to https
- Certs/Traefik: Remove previously generated certs when certs:generate event is removed from docker-compose.yml configuration

1.0.0-beta5 (2020-06-26)
------------------------

- Fixuid: Add Dockerfile generation when fixuid.yml file is created or deleted
- Docker: Add `docker.reverse_proxy.certresolver` to setup traefik certresolver globally
- Docker: Set `docker.restart_policy` default value to `unless-stopped` if `core.env.current` is different of `dev`
- Jsonnet: Add optional `router_rule` parameter to `ddb.VirtualHost` function in order to override the default `Host(hostname)`.
For traefik, available values in the [official documentation](https://docs.traefik.io/v2.0/routing/routers/#rule)
- Templates: Keep the file that match template target name when it has been modified since latest rendering ([#39](https://github.com/gfi-centre-ouest/docker-devbox-ddb/issues/39))

1.0.0-beta4 (2020-06-25)
------------------------

- Remove existing file or directory when generating a new file ([#31](https://github.com/gfi-centre-ouest/docker-devbox-ddb/issues/31))
- Docker: Fix missing `COMPOSE_PROJECT_NAME` and `COMPOSE_NETWORK_NAME` environment variables on ddb activate
- Jsonnet: Fix a bug when multiple Virtualhost are defined on the same docker-compose service


1.0.0-beta3 (2020-06-23)
------------------------

- Shell: Add aliases management


1.0.0-beta2 (2020-06-08)
------------------------

- Docker and Permissions features are now plugged on File feature
- Docker-compose locally mapped files/directories are now created on `ddb configure` to ensure valid user owning
- Fix Logging Error in chmod
- Upgrade chmod-monkey and use it everywhere to improve readability


1.0.0-beta1 (2020-05-12)
------------------------

- Add `git` feature. Currently, there is only one action : git:fix-files-permissions to update permissions for files 
based on git index. In order to update permissions of a file in git, use command 
```git update-index --chmod=+x foo.sh```. It can be disabled by setting ```git.fix_files_permissions``` to false in 
configuration.
- Add `--fail-safe` command line argument to stop on first error.
- Add `utils.process` module to help running external commands. It makes possible to configure path and additional 
arguments to any external process invoked by ddb.
- Default command line argument values can now be customized in configuration using `defaults` key.
- Fix and issue with traefik and jsonnet docker-compose when `networks` is defined in at least one service definition.
- Add `permissions` feature to apply chmod on some files.
- Add windows support for shell integration (cmd.exe only, powershell is still unsupported).

1.0.0-alpha1 (2020-05-10)
-------------------------

- First release, containing the following features: `certs`, `cookiecutter`, `copy`, `core`, `docker`, `file`, 
`fixuid`, `gitignore`, `jinja`, `jsonnet`, `run`, `shell`, `smartcd`, `symlinks`, `traefik`, `version`, `ytt`
