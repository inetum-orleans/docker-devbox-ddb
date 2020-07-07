Fixuid
===

One common pitfall when working with Docker is the file permissions management.
They are related to the way docker works and cannot really be fixed once for all.

In order to handle this the most easy and flexible way possible, we have integrated 
[fixuid](https://github.com/boxboat/fixuid).

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all git automations will be disabled.
    - type: boolean
    - default: False
              
- `url`: The URL to download the fixuid binaries.
    - type: string
    - default: https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz
    
??? example "Configuration example"
    ```yaml
    fixuid:
        disabled: false
        url: https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz
    ``` 
    
Automatic installation in service
---

In order to benefit from this feature, few steps are require. 

First things first, you need to create a file next to the Dockerfile.jinja in which fixuid will be integrated : 
`fixuid.yml`.
In this file, you will have to define three settings : 

- `user`: the user inside the container which will be used for running commands
- `group`: the group of the user inside the container which will be used for running commands
- `paths`: the list of paths in which you will work

For more details on this configuration, please refer to the 
[official documentation](https://github.com/boxboat/fixuid#specify-paths-and-behavior-across-devices) of fixuid

??? example "Example : A posgresql fixuid configuration"
    ```yaml
    user: postgres
    group: postgres
    paths:
      - /
      - /var/lib/postgresql/data
    ``` 
    
Then, in your `docker-compose.yml.jsonnet`, you will need to call for [ddb.User()](jsonnet.md#user) function from our 
library in order to add the right settings. 
 
Finally, run the `ddb configure` command in order to update the Dockerfile with instructions related with fixuid. 
It installs it in the image, and the entrypoint is changed to run fixuid before the default entrypoint.

!!! warning "For those not using templates and binary"
    Using this feature will update the Dockerfile in order to add the instructions needed for fixuid, which will need to 
    be added to your repository.
    
    Futhermore, in your docker-compose.yml, you will need to add the configuration `user` to the service using this 
    docker container.
    You will need to set it manually with the `uid` and `gid` of the host user which will run the container and execute 
    commands.