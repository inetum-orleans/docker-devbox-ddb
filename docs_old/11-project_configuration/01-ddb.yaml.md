ddb.yaml
===

docker-devbox-ddb provide a complete configuration from scratch which can be override in your project. 
You can see the current configuration by launching the given command : 
```
ddb config
``` 

In order to do so, you need to create a ddb.yaml in the root folder of your project.

In most cases, here are the variables you will need to override : 
```yaml
core:
  domain:
    sub: docker-devbox-ddb # The subdomain to use for the project. By default, it will be the name of the project directory
  env:
    current: dev # Current active environment (available list if the core.env.available variable)

docker:
  port_prefix: 372 # If you want to set the port_prefix for docker exposed ports

  registry: # The registry used for image storage. The following configuration will produce the "image" tag on service as following : hub.docker.io/foo/{servicename}
    name: hub.docker.io # The url of the repository
    repository: foo # The subfolder in the repository
```