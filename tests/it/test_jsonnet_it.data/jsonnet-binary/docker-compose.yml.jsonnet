local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
        node10: ddb.Image("node:10") +
                ddb.Binary("node", "/app", options="--version", options_condition='True') +
                ddb.Binary("npm", "/app", options="--version", options_condition='False'),
        node12: ddb.Image("node:12") +
                ddb.Binary("node", "/workdir", condition="'12' in cwd") +
                ddb.Binary("npm", "/workdir", condition="'12' in cwd"),
        node14: ddb.Image("node:14") +
                ddb.Binary("node", "/", exe=true) +
                ddb.Binary("npm", "/", exe=false),
         }
    })

