References
===

**ddb** is not tied to a particular language, framework or technical stack.

It's designed to automate application and docker configuration for a docker-compose based environment, so you forgot 
about the docker hard stuff while writing code, and so application can be deployed to stage and production environment 
with no changes on your sources.

The design of **ddb** is based around features. 
Those are triggered based on a system event on which they are listening, and sometimes they trigger new one themselves.

??? example Jsonnet
    When running `ddb configure`, there is a bunch of events triggered.
    
    This command raise the `phase.configure` events, which is intercepted by the [file](./feature/file.md) feature.
    This one scans folders and put found files one by one into an new event named `file.found`.
    
    Then, the [jsonnet](./features/jsonnet.md) feature interecept this `file.found` event and if it matches his 
    conditions trigger his behavior.
    
    And so on.
    
All the features created possessed at least one configuration, `disabled`, which let you decide if you want to enable it
or not.

Whether they are exposing more configuration or not, it will be organised under the name of the feature.

??? example "Example of docker"
    Example of [docker feature](docker#feature-configuration) configuration : 
    
    ```yaml
    docker:
      disabled: false
    ```