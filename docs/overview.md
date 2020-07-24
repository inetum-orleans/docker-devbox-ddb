Overview
===

Technology agnostic
-------------------

**ddb** is not tied to a particular language, framework or technical stack.

It's designed to **automate application and docker-compose configuration** on an environment, so you forgot 
about the docker hard stuff while writing code, and so application can be deployed to stage and production environment 
with no changes on your sources.

Features, actions and events
----------------------------

**ddb** make use of **features** to perform it's magic.

Each feature holds it's own **configuration** and embeds at least one **action**. An action brings at least one 
binding between an **event** and a **function**, so when this event occurs the function is called.

An action's function implementation can also raise other events that will trigger other feature action functions, 
making **ddb** a fully reactive software.

!!! question "What occurs when running ddb ?"
    When running `ddb configure` command, a bunch of events are triggered.
    
    Firstly, the command raise the `phase.configure` event, which is binded to the [file feature](./features/file.md).
    
    Secondly, [file feature](./features/file.md) scans files and triggers `file:found` event for each file in the 
    project directory.
    
    Thirdly, the [jsonnet](./features/jsonnet.md) feature which is binded to `file:found` event with a filter to match
    `.jsonnet` file extension only, so that only those files are processed by the jsonnet template engine.
    
    Other features perform actions the same way, like [jinja](./features/jinja.md), [symlinks](./features/symlinks.md) 
    and [ytt](./features/ytt.md) features.
    
    Those actions raises other events, like `file.generated` for each generated files, that will be processed by the 
    gitignore feature to add generated files to ignore list.    
        
    And so on.
