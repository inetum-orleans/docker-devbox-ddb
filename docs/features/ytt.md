ytt
===

TODO

Feature Configuration
---
- `disabled`: Definition of the status of the feature. If set to True, this feature will not be triggered.
    - type: boolean
    - default: False

!!! example "Configuration"
    ```yaml
    ytt:
      args:
      - --ignore-unknown-comments
      depends_suffixes:
      - .data
      - .overlay
      disabled: false
      extensions:
      - .yaml
      - .yml
      - ''
      includes:
      - '*.ytt{.yaml,.yml,}'
      keywords:
      - and
      - elif
      - in
      - or
      - break
      - else
      - lambda
      - pass
      - continue
      - for
      - load
      - return
      - def
      - if
      - not
      - while
      - as
      - finally
      - nonlocal
      - assert
      - from
      - raise
      - class
      - global
      - try
      - del
      - import
      - with
      - except
      - is
      - yield
      keywords_escape_format: '%s_'
      suffixes:
      - .ytt
    ```