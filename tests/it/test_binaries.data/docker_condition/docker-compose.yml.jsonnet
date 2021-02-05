local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
		node14: ddb.Image("node:14-alpine") +
			ddb.Binary("node"),
		node12: ddb.Image("node:12-alpine") +
			ddb.Binary("node", condition="'/node12' in cwd"),
		node10: ddb.Image("node:10-alpine") +
			ddb.Binary("node", condition="'/node10' in cwd")
	}
})
