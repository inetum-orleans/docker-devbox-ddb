SmartCD
===

The SmartCD feature provides automation to activate/deactive a ddb project environment.

Feature Configuration
---

- `disabled`: Definition of the status of the feature. If set to True, all SmartCD automations will be disabled.
    - type: boolean
    - default: False

!!! example "Configuration"
    ```yaml
    smartcd:
      disabled: false
    ```
    
SmartCD automation on Linux/Unix
---

Instead of manually launching the command `$(ddb run activate)` when you are entering a project folder and 
`$(ddb run deactivate)` when leaving it, you can install [cxreg/smartcd](https://github.com/cxreg/smartcd)
or [gfi-centre-ouest/smartcd](https://github.com/gfi-centre-ouest/smartcd) to automate this process.

As developers, we are lazy. So, we have automated generation of `.bash_enter` and `.bash_leave` files.
With this feature, you can cd from one project to another without thinking about updating environment 
variable as it does it for you.

This feature is enabled only if SmartCD is installed.
 
SmartCD automation on Windows
---

Sadly, we have not found any way to automate updates on environment when entering or leaving a folder on windows
environments.

As Windows is a bit onerous when it comes to generation of commands to execute, we have automated the generation of two
files : `ddb_activate.bat` and `ddb_deactivate.bat` in the root folder of your project. Those two files will execute the
environment updated commands needed to work on you project and switch to another one. 

The downside is that you must run them manually.




















