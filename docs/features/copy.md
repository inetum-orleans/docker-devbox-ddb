Copy
===

The `copy` feature is a simple way to automatically copy files from one folder to another. 

This feature is bounded to the [`init` command](../commands.md).

!!! summary "Feature configuration (prefixed with `copy.`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `disabled` | boolean<br>`false` | Should this feature be disabled ? |
    | `specs` | **Spec**[] | List of specifications of files/patterns to copy |

!!! summary "Spec configuration (used in `copy.specs`)"
    | Property | Type | Description |
    | :---------: | :----: | :----------- |
    | `source` | string<span style="color:red">*</span> | The source file to copy, or a glob expression matching files to copy. it can be a local file path, or it can starts with `http(s)://` to copy from a remote URL. |
    | `destination` | string<br>`.` | The exact target destination file or directory. |
    | `filename` | string | The destination filename. If empty and `destination` match a directory, `source` filename will be used. |
    | `dispatch` | string[]<br> | A list of directories or directory globs where the file will be duplicated. i.e if set to `['target']`, source file with be copied to `target` directory using filename defined in `destination` property. If set to ['target/*`], it will be copied in each subdirectory of target directory using filename defined in `destination` property. |

!!! example "Copy a file from an URL"
      ```yaml
      copy:
        specs:
          - source: 'https://github.com/boxboat/fixuid/releases/download/v0.5/fixuid-0.5-linux-amd64.tar.gz'
            destination: '.docker'
            filename: 'fixuid.tar.gz'
      ```
 
!!! example "Copy many files from filesystem"
    ```yaml
    copy:
      specs: 
        - source: '/etc/ssl/certs/*'
          destination: 'host-certs'
    ```
    