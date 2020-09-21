local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	"services": {
		"web": ddb.Build("web") + ddb.VirtualHost("80", "web.domain.tld") {
			"volumes": [
				ddb.path.project + "/.docker/web/nginx.conf:/etc/nginx/conf.d/default.conf:rw",
				ddb.path.project + ":/var/www/html:rw"
			]
		}
	}
})
