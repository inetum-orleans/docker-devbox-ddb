Dockerfile.jinja
===

In relation with the previous chapter, you still can define your own containers.

There is, once again, two ways of doing it : 
1- Create directly a static Dockerfile
2- Create a templated Dockerfile.jinja using the [jinja template engine](https://jinja.palletsprojects.com/en/2.11.x/)

Once you have created the file, you need to run the following command to generate the docker-compose : 
```
ddb configure
```

If you are working on a template file such as the docker-compose.yml.jsonnet, you can even use the watch option as following :
```
ddb --watch configure
```
This command will auto-recompile the templates file each time you update one 

Futhermore, if the gitignore feature is enabled, files generated from template will automaticaly be added to the .gitignore

This is also applicable to other type of files you want to dynamically generate using jinja template engine 

# Example 
```
TODO Ajouter un example
```

