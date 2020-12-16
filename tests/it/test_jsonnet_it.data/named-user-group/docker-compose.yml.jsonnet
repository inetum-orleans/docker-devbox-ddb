local ddb = import 'ddb.docker.libjsonnet';

ddb.Compose({
	services: {
        maven: ddb.Image("ubuntu") +
               ddb.User(uid=ddb.userNameToUid("root"), gid=ddb.groupNameToGid("nobody"))
              }
         })

