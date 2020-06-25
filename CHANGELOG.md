History
=======

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