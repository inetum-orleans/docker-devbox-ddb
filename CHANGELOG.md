History
=======

1.0.0-alpha2 (unreleased)
-------------------------

- Creation of feature *Git*<br/>
  Currently, there is only one action : git:fix-files-permissions which update umask for files based on git index. <br/>
  **Reminder :** in order to update the umask of a file in git, use command ```git update-index --chmod=+x foo.sh```<br/>
  It can be disabled by setting ```git.auto_umask``` to false in your project ddb.yaml file


1.0.0-alpha1 (2020-05-10)
-------------------------

- First release, containing the following features: `certs`, `cookiecutter`, `copy`, `core`, `docker`, `file`, 
`fixuid`, `gitignore`, `jinja`, `jsonnet`, `run`, `shell`, `smartcd`, `symlinks`, `traefik`, `version`, `ytt`