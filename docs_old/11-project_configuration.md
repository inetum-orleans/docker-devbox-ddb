Project Configuration
===

Three types of files are usefull for your project : 
1. [ddb.yaml](11-project_configuration/01-ddb.yaml.md)
2. [docker-compose.yml.jsonnet](11-project_configuration/02-docker-compose.yml.jsonnet.md)
3. [Dockerfile.jinja](11-project_configuration/03-Dockerfile.jinja.md)

Once you have configure the files you need and want, you will need to activate ddb in your current shell : 
```
$(ddb activate)
```

If you need to switch to another project, don't forget to deactivate it : 
```
$(ddb deactivate)
```

Or, if you have [smartcd](https://github.com/Toilal/smartcd) installed, you can create a .bash_enter and .bash_leave in order to automatically activate and deactivate ddb.