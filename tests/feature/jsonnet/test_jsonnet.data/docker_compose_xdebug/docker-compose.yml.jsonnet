local ddb = import 'ddb.docker.libjsonnet';

local user = "biometrie";
local password = "biometrie";

ddb.Compose({
	"services": {
		"php": ddb.Image("php:7.4-fpm")
		       + ddb.User()
		       + (if std.extVar('core.project.name') == 'xdebug3' then ddb.XDebug(version=3) else ddb.XDebug()),
	}
})
