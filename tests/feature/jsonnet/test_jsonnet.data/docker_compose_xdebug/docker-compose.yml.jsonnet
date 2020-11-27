local ddb = import 'ddb.docker.libjsonnet';

local user = "biometrie";
local password = "biometrie";

ddb.Compose({
	"services": {
		"php-default": ddb.Image("php:7.4-fpm")
		       + ddb.User()
		       + ddb.XDebug(),
		"php-xdebug2": ddb.Image("php:7.4-fpm")
		       + ddb.User()
		       + ddb.XDebug(version=2),
		"php-xdebug3": ddb.Image("php:7.4-fpm")
		       + ddb.User()
		       + ddb.XDebug(version=3),
	}
})
