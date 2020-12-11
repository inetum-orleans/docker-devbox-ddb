local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
	  apache: ddb.Image("httpd")
    }
})