CI Configuration
===

When you are using CI, if you want to use ```ddb``` functions, there is a few steps you need to follow :  
* set the ```SHELL``` environment variable to ```/bin/bash```
* install ddb :
```
curl -L https://github.com/gfi-centre-ouest/docker-devbox-ddb/releases/latest/download/ddb -o ddb && chmod +x ddb && sudo mv ./ddb /usr/local/bin/ddb
```  

Then you can run ddb commands in your pipeline