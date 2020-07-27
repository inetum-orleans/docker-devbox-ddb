Version
===

The version feature is a pretty simple one. 
It extracts information about the version of your project from git metadata.

Feature configuration
---

As all those values are extract from the git repository metadata, you can override it but it is not recommended.

- `disabled`: Definition of the status of the feature. If set to True, version feature will not be triggered.
    - type: boolean
    - default: False
- `branch`: The current branch of the project
    - type: string
    - default: <the current git branch>
- `hash`: The hash of the current commit
    - type: string
    - default: <the current commit hash>
- `short_hash`: The short version of the hash of the current commit
    - type: string
    - default: <the current commit hash short version>
- `tag`: The current git tag
    - type: string
    - default: <the current git tag>
- `version`: The current version
    - type: string
    - default: <the current version of the repository>
    
!!! example "Configuration"
    ```yaml
    version:
      branch: master
      disabled: false
      hash: c8a21135dab1fbb3b994bc2d5a374e2f5477ddfa
      short_hash: c8a2113
      tag: null
      version: null
    ```