local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
        maven: ddb.Image("ubuntu") +
               ddb.User(uid=ddb.userNameToUid("$invalid-user!"), gid=ddb.groupNameToGid("$invalid-group!"))
              }
         })

