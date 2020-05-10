History
=======

1.0.0-alpha2 (unreleased)
-------------------------

- Add `git` feature. Currently, there is only one action : git:fix-files-permissions to update permissions for files 
based on git index. In order to update permissions of a file in git, use command 
```git update-index --chmod=+x foo.sh```. It can be disabled by setting ```git.fix_files_permissions``` to false in 
configuration.


1.0.0-alpha1 (2020-05-10)
-------------------------

- First release, containing the following features: `certs`, `cookiecutter`, `copy`, `core`, `docker`, `file`, 
`fixuid`, `gitignore`, `jinja`, `jsonnet`, `run`, `shell`, `smartcd`, `symlinks`, `traefik`, `version`, `ytt`