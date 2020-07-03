CI Configuration
===

When you are using CI, if you want to use ```ddb``` functions, there is a few steps you need to follow :  
* set the ```SHELL``` environment variable to ```/bin/bash```
* install ddb
* execute ```ddb configure```

Then you can run ddb commands in your pipeline

Here are some links to help you :
1. [Azure Devops DDB Install Template](./20-pipeline_configuration/azure/install.yml)