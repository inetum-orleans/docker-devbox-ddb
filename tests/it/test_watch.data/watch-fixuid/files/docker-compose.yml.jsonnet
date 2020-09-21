local ddb = import 'ddb.docker.libjsonnet';


ddb.Compose({
	services: {
	  db: ddb.Build("db") +
	      ddb.User()
	      }
})
