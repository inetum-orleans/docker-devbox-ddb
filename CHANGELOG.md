History
=======

<!--next-version-placeholder-->

## v2.0.0 (2023-10-16)

### Feature

* Always specify the docker-compose.yml file in docker run ([#224](https://github.com/inetum-orleans/docker-devbox-ddb/issues/224)) ([`3f756de`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/3f756de12786f3ca48ddddc97cac02e2e6a840a7))

### Fix

* **tests:** Replace docker-compose with python-on-whales ([#227](https://github.com/inetum-orleans/docker-devbox-ddb/issues/227)) ([`52c2bce`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/52c2bce66edb06c9c961a06db1cd15142037597a))
* **doc:** Fix XDebug typo in doc ([`25a87f3`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/25a87f3f49a5e72b572fbdcfd45a2f43ed8c1d0d))
* **doc:** Links to docker-devbox should go on the correct repo ([`2bee946`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/2bee946471778db3a545fe6ba2a0c11a2a846aca))
* **tests:** Unset local variable override to allow local tests ([`09f7caa`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/09f7caad6df9deda356b00d1091532cd37b1ac60))
* **ci:** Remove deprecated docker-compose dependency ([`714da68`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/714da68456bb1b463b155a96f39c98d7ce9b9691))
* **ci:** Use python-semantic-release < 8 for now ([`f51174d`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/f51174d4a1c8679952f14c5cfb458cbe3f606372))
* **readme:** Replace compose v1 with v2 ([`b63fdd0`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b63fdd00641f47c59e87dfb39512c0ca202f6b7d))
* **tests:** Fixed tests related to the recent ddb run modification ([`cf0376f`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/cf0376fc9d1db5cd4ccfcdccdcaa48ea47345353))
* **pylint:** Disable false-positive pylint warning ([`cb460c9`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/cb460c951b6f50ee285025ba0e6a388eb0c534bd))
* **doc:** Fixed typo in symfony sample ([`ffb8f19`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/ffb8f1916c559f3392bed8164a734f333fc54117))

### Breaking

* remove support for ubuntu 18 ([`b2ff624`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b2ff6248389e966e4a608f55e5b710deb0a2c60c))

## v1.17.0 (2023-02-18)
### Feature
* **dependencies:** Add python 3.11 support ([`e6fcd6a`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e6fcd6a030db8a4fd47428db58cfb27cb10b17f4))

### Fix
* **shell:** Replace tempfile with mktemp to remove the deprecation warning ([`46329df`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/46329df2b83db57e4696faab54c8b2a3bd88f225))

## v1.16.0 (2022-10-13)
### Feature
* **file:** Add `**/.yarn` to `file.excludes` default value ([`5ccfb47`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5ccfb470c031e471e2fb763b756221dc8aa604d1))
* **windows:** Improve windows support ([`2aded1f`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/2aded1f9e25dde0467659499cfe92c3ac4082444))
* **docker:** Add docker compose v2 support ([`d1d522b`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/d1d522bffb1b38160abe9eeb9dfb6d44dc615f5f))
* **docker:** Set `docker.ip` fallback to `127.0.0.1` ([`5d0afb8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5d0afb8a056d2471ae1841413b5bb426ba336a33))

### Fix
* **windows:** Fix invalid mapPath in libjsonnet ([`74ef98a`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/74ef98a56ff5366a50cb1afca96b6a4a0d168436))
* **docker:** Sort path mapping in both python and jsonnet ([`e9d53e3`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e9d53e32c184fa450d020dc84866b2bf4bed7857))

### Performance
* **file:** Improve performance of file walker ([`6bf49ea`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/6bf49eac9926c8f57b88ef7a2dae183ef0c8435e))

## v1.15.6 (2021-11-09)
### Fix
* **run:** Wrap $@ in single quote to echo command in temporary file ([`d5ee3a2`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/d5ee3a2f5693c9151e38d1186f19e0678c37cf43))

## v1.15.5 (2021-11-09)
### Fix
* **run:** Fix DDB_RUN_OPTS handling to quote arguments properly ([`e91a168`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e91a16817f77c7652439dc7ad005b1e13a9ac63d))

## v1.15.4 (2021-11-05)
### Fix
* **shell:** Fix invalid generated binary shims ([#213](https://github.com/inetum-orleans/docker-devbox-ddb/issues/213)) ([`5301003`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5301003e44edef14884bc8f3897960e251855469))

## v1.15.3 (2021-11-05)
### Fix
* **shell:** Improve binary shim by generating temporary file ([#211](https://github.com/inetum-orleans/docker-devbox-ddb/issues/211)) ([`22046e9`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/22046e934778f4c95c78105164ea59ba0b3ed655))

## v1.15.2 (2021-10-18)
### Fix
* **core:** Use tag instead of version to build release url ([`446b140`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/446b14046fb2da93ee89460bc44d54ebdb4738da))
* **copy:** Fix copy when used in a subdirectory ([`602086b`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/602086b5492bda2ff437c24ba44137cb77225b0b))

## v1.15.1 (2021-10-14)
### Fix
* **fixuid:** Enhance verbosity and user messages ([`3668379`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/366837987b0ab002189c57d561b1c249a85489e2))

## v1.15.0 (2021-10-14)
### Feature
* Drop ubuntu 16.04 support for binary ([`7335a5c`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/7335a5c59f1b6da6a1c2873469c8a9b96279d50e))
* **fixuid:** Use docker cli instead of docker-py ([`cba2394`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/cba2394a0393e5e4127a1b9e48090ee75d34d505))

### Fix
* **fixuid:** Use fixuid v0.5.1 ([`0fd82e1`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0fd82e10d58168c17304c964a006f90d1beafd8e))

## v1.14.0 (2021-08-04)
### Feature
* **jsonnet:** Generate compose network name without underscore ([`4b6c139`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4b6c139b151c8b10f06a220f343eb57322a61e3f))

### Fix
* **jsonnet:** Replace dots with dash in traefik labels ([#205](https://github.com/inetum-orleans/docker-devbox-ddb/issues/205)) ([`9a79b7b`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/9a79b7b7eecc9d0101011cb5e4d03a1a39b73c2c))
* **jsonnet:** Remove duplicate _default in COMPOSE_NETWORK_NAME env var ([`0c2113a`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0c2113af98e854f325e33b4f67b9095513b55eb8))

## v1.13.3 (2021-04-01)
### Fix
* **run:** Use avoid_stdout in ddb run command ([#204](https://github.com/inetum-orleans/docker-devbox-ddb/issues/204)) ([`589cb13`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/589cb13bbea3ff5ebaa04d4f08efa6c303f1143d))

### Documentation
* **binaries:** Add DDB_RUN_OPTS note ([`5425efe`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5425efe86f6b6f5aefa73da55c9f158824486c66))

## v1.13.2 (2021-03-24)
### Fix
* **binary:** Binary is now registered again when condition is changed ([`fd5230b`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/fd5230b0edaae574a0ed0107388206a9bd25bac9))

### Documentation
* **binaries:** Typo in docker compose command ([`88ab7b0`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/88ab7b0608dc788dc3ceefaa9cd9faaaf3051491))

## v1.13.1 (2021-02-24)
### Fix
* **self-update:** Fix permission issues with self-update command ([#146](https://github.com/inetum-orleans/docker-devbox-ddb/issues/146)) ([`4cd8bce`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4cd8bcedda3f0b92653419b2939474855a7bc169))

### Documentation
* **faq:** Add ddb-linux-older-glic edition note ([`895742b`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/895742b06670871e55e892357ffe3cffb3bf1f94))

## v1.13.0 (2021-02-24)
### Feature
* **core:** Add release_asset_name to customize asset to download on update ([`e2b3324`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e2b3324b2279f0c9c960263bedc1f86588e4052c))

### Documentation
* Update FAQ ([`4cea4bf`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4cea4bfd6e6e89ce81206d1bd810e51850314398))
* Remove defaults, add Djp packages and Binaries pages ([`0ebc892`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0ebc89284c47722d3de4e7871702385ec86b28db))
* **jsonnet:** Add missing jsonnet.docker.compose configuration properties ([`5941a46`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5941a461b0f7dc9c42a81fd20e6ce5dc5a897874))

## v1.12.0 (2021-02-19)
### Feature
* **config:** Add more capabilities to config command ([`89d20d6`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/89d20d6cecfe7b9189cda46e61171c94c5998ef3))

### Fix
* **jsonnet:** Remove client_port=9000 for xdebug3 configuration ([`d8ca959`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/d8ca959e4a88eb4ec3791bb5d50e926c91a40a95))
* **jsonnet:** Set log_level=0 to xdebug3 configuration ([`689efb0`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/689efb0851841eb43e0a3b62e0f3d7fd8cd5a1ba))

## v1.11.0 (2021-02-17)
### Feature
* **run:** Add `DDB_RUN_OPTS` support to add docker-compose options on ddb run ([`b1aca49`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b1aca49abc85cfd0ede6d432430937fe4f5cdb82))

### Fix
* **core:** Disable core.check_updates after running self-update command ([`6274317`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/62743171b9868341f6ba9270fff39a938d11f5d8))

## v1.10.3 (2021-02-15)
### Fix
* **alpine:** Add Alpine Linux support ([`bcf04b5`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/bcf04b523482de438742e51d47198464d00f0553))

## v1.10.2 (2021-02-15)
### Fix
* **package:** Fix binary package error `NameError: name 'help' is not defined` ([`b066513`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b0665139196e0b9e035e8c66c6b28ca8bc419eda))
* **package:** Fix binary package error `NameError: name 'help' is not defined` ([`47bf72c`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/47bf72c88a4bbe12cf553ab9d186b0b00844dcc5))

## v1.10.1 (2021-02-15)
### Fix
* **core:** Use new binary names for self-update ([`56fc5ab`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/56fc5abfdb97a5750a504789c378561646e6d92f))

## v1.10.0 (2021-02-15)
### Feature
* **jsonnet:** Add mount options to mount named volumes inside project directory ([`401c9bd`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/401c9bd7bc12060dc2514001fbd198eec443792f))
* **config:** Add `core.check_updates` configuration ([`3a779a4`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/3a779a45c453f85ebe2e9f17b6d2ef51179786a1))

### Fix
* **traefik:** Stop using deprecated properties internally ([`d3f06d8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/d3f06d8cadf48089a2cef2995959eb74e8c0ce50))
* **selfupdate:** Display detected binary path on permission error ([`c0cfe91`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/c0cfe910c1a80824804250a6b10b1b3776b25b28))

## v1.9.2 (2021-02-09)
### Fix
* **fixuid:** Fix automatic fixuid configuration for some Dockerfile ([`f504416`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/f504416b4f10f62f98a87e23d6c1cd13ed6eb3b9))
* **binary:** Use COMPOSE_IGNORE_ORPHANS=1 in global binary shim ([`9d4a955`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/9d4a9556305d04031cdf0d10b52eb3e4ee5fb504))
* **binary:** Fix orphan containers when using global binaries ([#195](https://github.com/inetum-orleans/docker-devbox-ddb/issues/195)) ([`40b3cae`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/40b3cae12450e1897496658d3f62ceb814087e00))

## v1.9.1 (2021-02-08)
### Fix
* **jsonnet:** Add missing ddb.feature.jsonnet.docker package in exe version ([`5253802`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5253802f45bcc7a2462ae54ba2f6192afdab25a8))

## v1.9.0 (2021-02-05)
### Feature
* **jsonnet:** Add port conflict solver as jsonnet postprocessor ([`0c7bd16`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0c7bd165dabaf4b9d1338f1fd436b4fada0bc1c6))

## v1.8.1 (2021-02-05)
### Fix
* **jsonnet:** Add configurable default value for Binary global flag ([`ed444eb`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/ed444eb166c6b008f8aabd3a7bb5928de639cdf7))
* **gitignore:** Avoid addition of global binaries in .gitignore ([`15f95f4`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/15f95f413d03262fb2255a5f222fbe16ed20143d))

## v1.8.0 (2021-02-05)
### Feature
* **config:** Enhance config command output and add options ([#189](https://github.com/inetum-orleans/docker-devbox-ddb/issues/189)) ([`02dbcb5`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/02dbcb51808b5891efd3a39468ccf3f2dfcfdbe2))
* **binary:** Add global and entrypoint options to binaries ([#185](https://github.com/inetum-orleans/docker-devbox-ddb/issues/185)) ([`61f973c`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/61f973ca721c470936b14a35363c3541c15b1c03))

### Fix
* **file:** Add .idea directory to default excludes ([`24d3df7`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/24d3df7500c9222afe8a23038e83182ade424caf))
* **jsonnet:** Add support for volume starting with an environment variable ([`e4f2bcb`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e4f2bcb726f826cd60e9a24957ab389e8eff560a))
* **gitignore:** Check if file is gitignore before trying to remove it ([#190](https://github.com/inetum-orleans/docker-devbox-ddb/issues/190)) ([`4cbcdec`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4cbcdec05a92b5b0bc6d1ef2902c5114b29c3291))

## v1.7.3 (2021-02-04)
### Fix
* Add missing extensions in binary bundle ([#187](https://github.com/inetum-orleans/docker-devbox-ddb/issues/187)) ([`63febce`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/63febce6c474e958cc56eeddad254af36adb1b30))

## v1.7.2 (2021-02-03)
### Fix
* **jinja:** Fix extra EOL issue when deprecated property are used ([`13c2d0e`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/13c2d0e92efad9ccd6ceb845b92c7f422c29b734))

## v1.7.1 (2021-02-03)
### Fix
* **gitignore:** Sort gitignore entries to avoid conflicts ([`071fedd`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/071fedde1d89538d3d22765259b7d8f2ade8c117))

## v1.7.0 (2021-02-03)
### Feature
* **cookiecutter:** Add .patch files support in cookiecutter feature ([`3b20434`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/3b204348709348f45636c31cc5e0a78a636b3e09))
* **djp:** Add djp packages support through cookiecutter feature ([`15938ec`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/15938ecd7e723c7bf7e41318db073cc35255bee8))
* **jsonnet:** Enhance `ddb.docker.libjsonnet` to support future djp packages ([`a48c5a9`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/a48c5a9040627379b82da8556125c2eff52aec7a))
* **core:** Add `core.domain.value` read only property ([`ab4001e`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/ab4001e84b40a6b80fa3f2697043bae9ac97c505))
* **jsonnet:** Add `ddb.env.current` and `ddb.env.available` ([`edaef0a`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/edaef0a5ef3c1d329c8bbeae0617f55bed61f262))

### Fix
* **autofix:** Make `--autofix` less intrusive and fix variables only ([`70389db`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/70389dbb1da802502d0adb84657acf4eb64cf2d0))
* **jinja:** Autofix now fix templates in code blocks only ([`8575f79`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/8575f7911d3a4413936a73199000fccf7306340a))
* **inetum:** We are Inetum, mais Orléans quand même :) ([`f2e85ea`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/f2e85eab75c68c24610f102f83de5cf9a7856c85))
* **inetum:** We are Inetum, mais Orléans quand même :) ([`5281071`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5281071f280164fe7c3eb6782da44557c46f4104))

### Documentation
* **index:** Update badges ([`39cd66b`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/39cd66becebdfd88dbcfe43ed23d631fb76a902b))

## v1.6.1 (2021-01-20)
### Fix
* **migration:** Add boolean value support fr docker.reverse_proxy.type migration ([#184](https://github.com/inetum-orleans/docker-devbox-ddb/issues/184)) ([`682f23f`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/682f23fb2d796d3651986faa1eec2c5c329434a6))

## v1.6.0 (2021-01-19)
### Feature
* **jinja:** Add configuration options to jinja Environment ([#181](https://github.com/inetum-orleans/docker-devbox-ddb/issues/181)) ([`092d9d0`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/092d9d09caf4f13b0c8295a47e8148a2bc38c3af))
* **scope:** Refactor configuration schemas with autofix (#164 #179) ([`10b7a72`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/10b7a72e018c925970002e5497468eef43cba50b))

### Fix
* **config:** Fix deprecations warnings and backward compatibility ([`6ab20c2`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/6ab20c2590bab03865930330b5812c6376348f84))

### Documentation
* **usage:** Update usage output in docs ([`4ebb752`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4ebb75207768efe6323a00acfd50dc25833d60af))

## v1.5.1 (2021-01-15)
### Fix
* **binary options:** Fix an issue introduced by #141 ([`f404353`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/f4043538e01b7761828212196b2d15128f6b1fba))

## v1.5.0 (2021-01-14)
### Feature
* **configure:** Ensure project configuration file is available before configure ([#170](https://github.com/inetum-orleans/docker-devbox-ddb/issues/170)) ([`bd1c814`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/bd1c814a2e2c847685bfe49134dd886dbcb51eda))
* **file:** Add `target/` and `dist/` directories to default excludes ([`9b7b467`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/9b7b46770513c4121c52301bb7c80bd2f0463e6a))
* **binaries:** Allow many binaries to be registered for the same name ([#141](https://github.com/inetum-orleans/docker-devbox-ddb/issues/141)) ([`b3d8cd8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b3d8cd823cb3a90beec013e4943f7e007182aad5))
* **permission:** Copy permission from template file to target ([#147](https://github.com/inetum-orleans/docker-devbox-ddb/issues/147)) ([`8595c9f`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/8595c9f5ae4999244dcdf8f6896398e764399c9f))
* **devbox:** Prepare next release of docker-devbox with retro-compatibility ([`fdfbc24`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/fdfbc245abc94facbf21e2e92d8a20c05ed6058f))
* **jsonnet:** Add Expose function in ddb.docker.libjsonnet ([`dffcab1`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/dffcab1566e3f055a61872ea0d4097c6f9c571e4))

### Fix
* **shell:** Fix drive case for default Windows `docker.path_mapping` ([#159](https://github.com/inetum-orleans/docker-devbox-ddb/issues/159)) ([`a3e2c09`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/a3e2c09472d73ee6507623dd048958f11015addb))
* **shell:** Use `_` instead of `-` to sanitize environment variable name ([#160](https://github.com/inetum-orleans/docker-devbox-ddb/issues/160)) ([`f9e11a8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/f9e11a8515c653246753d55183e9adf50cd542a8))
* **shell:** Add support for relative paths in shell.path.directory ([#168](https://github.com/inetum-orleans/docker-devbox-ddb/issues/168)) ([`6f4f938`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/6f4f938a0b814084bb2922f9a683427f9020a801))
* **main:** Clear cache when an unexpected error occurs ([#169](https://github.com/inetum-orleans/docker-devbox-ddb/issues/169)) ([`8c0940a`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/8c0940a4cd2436bd78870635fe871b600ba9bb5d))
* **binary options:** Fix an issue introduced by #141 and force lf ([`76c7bf2`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/76c7bf2640c04274b72981d60605bc9352eb764f))
* **shell:** Move PWD environment exclude to configuration ([`848ec99`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/848ec99b90386aab09784d5f1870260173ac3ed3))
* **traefik:** Check domain is not empty when rule is empty ([`33bd166`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/33bd1667169ccb7a4ef9217a42b7865ab0601a0c))

### Documentation
* **style:** Enhance docs style for all configuration properties and examples ([`9c396d5`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/9c396d50ddcc14a95f613636f7d0464d601edc0d))
* **jsonnet:** Add session parameter to XDebug documentation ([`5febad8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/5febad815c1812016b8fa3117c08e2d32dfb735c))

## v1.4.4 (2020-12-30)
### Fix
* **bash:** Exclude PWD environment variable from backup/restore ([#142](https://github.com/inetum-orleans/docker-devbox-ddb/issues/142)) ([`e8ee977`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e8ee9771b5c63b893a07fb0e1690dac21cdafa6f))
* **update:** Fix can only concatenate str (not "list") to str ([#143](https://github.com/inetum-orleans/docker-devbox-ddb/issues/143)) ([`0348407`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0348407b0e457b8ea56320b30592b5367086bab5))

## v1.4.3 (2020-12-22)
### Fix
* **dependencies:** Remove docker-compose dependency ([#140](https://github.com/inetum-orleans/docker-devbox-ddb/issues/140)) ([`ac12c8a`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/ac12c8aec29965abf72d5747698ad97bde3cc850))
* **core:** Fix self-update command error on file replace ([#138](https://github.com/inetum-orleans/docker-devbox-ddb/issues/138)) ([`97e4f81`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/97e4f81d799fb5617a82dce8b9d533d5b489cae1))
* **changelog:** Fix changelog ([`9507778`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/9507778794186ebf7864f7ebaaad6e7e9ea3ce9d))
* **fixuid:** Remove print scrap ([`dad030f`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/dad030f748b066021bc28d078e2ca939af1ca73e))

## v1.4.2 (2020-12-21)
### Feature
* **fixuid:** Add Dockerfile comments to disable or customize fixuid automic configuration ([`e855efc`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/e855efcce49e0c66994e43f522a9f85e129df7f3))

### Fix
* **file:** File scan now yield directories so you can use permission on directories ([`eb232d8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/eb232d85549c76e1d753b90c09727d3804ba9443))
* **file:** Fix recursive=False parameter in FileWalker ([`c81fd76`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/c81fd76874922bf12b18a89ee729930fd0e0a83e))

### Documentation
* **setuptools:** Update python versions in classifiers ([`4012cbf`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4012cbf2ca2298496ff2438f82736c21ba17a776))

## v1.4.1 (2020-12-17)
### Fix
* **core:** Fix self-update command ([`843cf67`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/843cf6736dff9290ececc39334a23c2a2446b3c3))

## v1.4.0 (2020-12-17)
### Feature
* **core:** Add `core.required_version` parameter to enforce project ddb version requirement ([#75](https://github.com/inetum-orleans/docker-devbox-ddb/pull/75)) ([`bbf32e6`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/bbf32e61353121332870e3670d84d647fa7df812))
* **main:** Add main:start event ([`8764d01`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/8764d013a7642beb900e7d2333c974c87b0d11d8))
* **self-update:** Add self-update command to update binary from github ([#131](https://github.com/inetum-orleans/docker-devbox-ddb/pull/131)) ([`0171f37`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0171f37fcd1dfd6c1f93d8bec2aa4f9608542bec))
* Add Python 3.9 support and drop Python 3.5 support ([`83e97e9`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/83e97e94d053d3338b1307f7e491c12e5c6683c3))

### Documentation
* **self-update:** Add docs for the new self-update command ([`86b5ef8`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/86b5ef8467af0e45b6b176c42553f9cc77c99a99))
* **contributing:** We are now using github actions and semantic release ([`b4f1127`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b4f11276a37a4e4b1142f6b54b3d0763ccf5639e))

## v1.3.1 (2020-12-16)
### Fix
* **version:** Version check now removes "v" first character from tag ([#129](https://github.com/inetum-orleans/docker-devbox-ddb/pull/129)) ([`71a3567`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/71a3567e58e3a0a93b279c83668275a1c64a72f5))

## v1.3.0 (2020-12-16)
### Feature
* **docker:** Add https option to reverse-proxy features (libjsonnet and configuration) ([`c2c1fad`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/c2c1fad347a338d38b3f9cd4e16bf4d634d72741))
* **docker:** Add support for named user and group ([`62ab647`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/62ab647872360b06c0b644513021d890e5173291))
* **configuration:** Add insert/insert_if_missing merge strategies. ([`00d62b9`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/00d62b9fdfd9d150f9574f04419fc620d644ff25))
* **configuration:** Add core.configuration.extra to include additional configuration files ([`b7d30de`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b7d30de2ba9ec73b8e36dc96143adb8f10185730))
* **xdebug:** Add more parameters to XDebug jsonnet function ([`cf5dc74`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/cf5dc742399061034fa17d86c2f3b69b380adee1))
* **JSonnet:** Add support for XDebug 3 ([`6bc337c`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/6bc337c98d27925f40e55386f41748ba749d54cf))

### Fix
* **docker:** Add tests and fix issues with named user and group ([`b88470c`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/b88470c43d381b6093b609d7064042fac8af78db))
* **shell:** Slufigy environment variable names ([`0513038`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/0513038b3bab499d2bf681e2e012c3fb867bd629))
* **copy:** Correction du NoneType error ([`4b798bd`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/4b798bd733c9dbf770961cb3127452611d2a6850))
* **docs:** Fix typo for excludes configuration properties ([`d0cda14`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/d0cda1490d2e82b2bd5330d46f507b1f75a6c814))

### Documentation
* **changelog:** Reformat changelog ([`7440081`](https://github.com/inetum-orleans/docker-devbox-ddb/commit/744008161fc4f22035e0436427b4e8475dc9f69f))

## v1.2.3 (2020-11-13)

- Jsonnet: Add "JoinObjectArray" method.
- Jsonnet: Add `path_prefix` option for a VirtualHost.
- Docker: Add `docker.reverse_proxy.redirect_to_path_prefix` which force redirection to `path_prefix` if defined on a
  VirtualHost.
- Traefik: Add `path_prefix` option for a service.
- Traefik: Add `redirect_to_path_prefix` option for a service which force redirection to `path_prefix` if defined on the
  service.
- Docker: Add configurations for `docker-compose.yml` generation (`file_version`, `service_init` and `service_context_root`).

## 1.2.2 (2020-10-21)

- Docker: Add `docker.build_image_tag_from` and deprecates `docker.build_image_tag_from_version`.
- Watch: Fix file exclusion issues when an ancestor directory is excluded
- Gitignore: add first slash to set full relative path of file added to the gitignore
- Docker Binary: Check if the container is up if user run "ddb run <binary>" on a command flagged "exe". If it is down,
  it will be launch.

## 1.2.1 (2020-10-06)

- Jsonnet: Add ServiceName function available globally.
- Core: Avoid `--eject` to delete files outside of project directory.

## 1.2.0 (2020-10-03)

- Core: Add `--eject` option to `configure` command. This option can be used to convert the project to a static version 
  and detach it from ddb.
- Info: Add `traefik.extra_services` to `ddb info` command output.
- Gitignore: Gitignore feature is now disabled by default on non-dev environment.

## 1.1.1 (2020-09-22)

- Build: Fix `ModuleNotFoundError: No module named 'compose'` error in binaries built of ddb.

## 1.1.0 (2020-09-21)

- Docker: Add `--rm` flag to docker-compose run command in binaries.
- Version: Fix `version.branch` value when using a detached repository and head refs many branches. If no branch is 
reported in `refs/head`, it will use `refs/remote/origin` to get branche name.
- Config: Lists merge strategy is now defined as `override` by default.
- Config: Add support for `merge`/`value` inside configuration to control merge behavior between configuration files.
- Config: Add support for `ddb.<env>.yml` configuration file based on `core.env.current` value.

## 1.0.9 (2020-09-12)

- Traefik: Use Jinja template for `ssl_config_template` parameter (Jinja context match the ddb.yml configuration).
- Traefik: Add `extra_services` in `traefik` feature. Extra service allow to configure a service running 
  outside of the docker stack inside traefik, so it's included in the docker network and still benefits of 
  docker-devbox features (domain name, SSL certificates, ...).
- Version: Make detached repo report the effective branch instead of `HEAD`.


## 1.0.8 (2020-09-10)

- Config: Fix issues with custom config parameters.
- Shell: Raise an error when activate/deactivate was already called.

## 1.0.7 (2020-09-09)

- Config: Fix overriding of default values with `DDB_OVERRIDE_*` environment variables.
- Core: Use `toilal/pyinstaller-linux` and `toilal/pyinstaller-windows` docker images to build binaries.

## 1.0.6 (2020-09-09)

- Copy: Add `file:generated` events on copy to add copied files in `.gitignore`.
- Copy: Run copy feature on each `ddb configure` command instead of a single time.
- Shell: Use `.` instead of `source` to make `/bin/sh` work properly.
- Shell: Add `check-activated` command and avoid issues when activating the project many times.

## 1.0.5 (2020-09-07)

- Jsonnet: Fix `duplicate field name` error when sharing a named volume on many docker-compose services.
- Certs: Add creation of `.signer.crt` to help automation of signer TLS Certificate configuration in the project.


## 1.0.4 (2020-09-04)

- Shell: Fix binary shims when `-h`/`--help` is given as argument.
- Core: Add the `info` command which output compacted information about docker containers such as environment 
  variables, virtual host, exposed ports and binaries.
- Jsonnet: Fix `cache_from` value for docker services to match the `image` one 
- Fixuid: Enhance fixuid configuration when image has no entrypoint defined.
- Config: Add support for `ddb.yml` configuration watch. If a project configuration file changes, configuration is 
reloaded and command is runned again to update all generated files. It currently doesn't watch configuration files 
from ~/.docker-devbox nor ~/.docker-devbox/ddb directories as it's based on `file` feature events.


## 1.0.3 (2020-09-01)

- Certs: Fix inversion between certificate and key for `certs:generated` and `certs:available` events.


## 1.0.2 (2020-08-28)

- Core: Fix `[Errno 11] Resource temporarily unavailable` error when running more than one instance of ddb.
- Aliases: Fix global aliases for projects lying inside docker devbox home directory (traefik, portainer, cfssl).

## 1.0.1 (2020-08-25)

- Docker: Limit `port_prefix` to  `655` instead of `1000` to avoid *invalid port specification* error.


## 1.0.0 (2020-08-25)

- Binaries: Fix docker binary workdir value
- Shell: Add `global_aliases` configuration option to generate aliases inside global docker devbox home.


## 1.0.0-beta9 (2020-08-20)

- File: Emit delete events before found events.
- Core: Set working directory to project home.
- Fixuid: Upgrade fixuid to v0.5.


## 1.0.0-beta8 (2020-08-10)

- Binary: Add exe option to use docker-compose exec instead of run
- Gitignore: Add enforce option to force addition of file to gitignore
- Certs: Add `certs.cfssl.append_ca_certificate` and `certs.cfssl.verify_checksum` options support
- Core: Add release check on --version
- Core: Fix crash when github quota has exceeded on release check

## 1.0.0-beta7 (2020-07-25)

- Add MacOS support (no binary package available though)
- Shell: Add zsh support
- Jsonnet: Fix an issue when reverse proxy is not defined to traefik.
- Docs: Add way more docs

## 1.0.0-beta6 (2020-07-03)

- Windows Shell: Fix alias generation
- Jsonnet: Add `redirect_to_https` to ddb.VirtualHost in order to redirect http requests to https
- Certs/Traefik: Remove previously generated certs when certs:generate event is removed from docker-compose.yml configuration

## 1.0.0-beta5 (2020-06-26)

- Fixuid: Add Dockerfile generation when fixuid.yml file is created or deleted
- Docker: Add `docker.reverse_proxy.certresolver` to setup traefik certresolver globally
- Docker: Set `docker.restart_policy` default value to `unless-stopped` if `core.env.current` is different of `dev`
- Jsonnet: Add optional `router_rule` parameter to `ddb.VirtualHost` function in order to override the default `Host(hostname)`.
For traefik, available values in the [official documentation](https://docs.traefik.io/v2.0/routing/routers/#rule)
- Templates: Keep the file that match template target name when it has been modified since latest rendering ([#39](https://github.com/inetum-orleans/docker-devbox-ddb/issues/39))

## 1.0.0-beta4 (2020-06-25)

- Remove existing file or directory when generating a new file ([#31](https://github.com/inetum-orleans/docker-devbox-ddb/issues/31))
- Docker: Fix missing `COMPOSE_PROJECT_NAME` and `COMPOSE_NETWORK_NAME` environment variables on ddb activate
- Jsonnet: Fix a bug when multiple Virtualhost are defined on the same docker-compose service


## 1.0.0-beta3 (2020-06-23)

- Shell: Add aliases management


## 1.0.0-beta2 (2020-06-08)

- Docker and Permissions features are now plugged on File feature
- Docker-compose locally mapped files/directories are now created on `ddb configure` to ensure valid user owning
- Fix Logging Error in chmod
- Upgrade chmod-monkey and use it everywhere to improve readability


## 1.0.0-beta1 (2020-05-12)

- Add `git` feature. Currently, there is only one action : git:fix-files-permissions to update permissions for files 
based on git index. In order to update permissions of a file in git, use command 
```git update-index --chmod=+x foo.sh```. It can be disabled by setting ```git.fix_files_permissions``` to false in 
configuration.
- Add `--fail-safe` command line argument to stop on first error.
- Add `utils.process` module to help running external commands. It makes possible to configure path and additional 
arguments to any external process invoked by ddb.
- Default command line argument values can now be customized in configuration using `defaults` key.
- Fix and issue with traefik and jsonnet docker-compose when `networks` is defined in at least one service definition.
- Add `permissions` feature to apply chmod on some files.
- Add windows support for shell integration (cmd.exe only, powershell is still unsupported).

## 1.0.0-alpha1 (2020-05-10)

- First release, containing the following features: `certs`, `cookiecutter`, `copy`, `core`, `docker`, `file`, 
`fixuid`, `gitignore`, `jinja`, `jsonnet`, `run`, `shell`, `smartcd`, `symlinks`, `traefik`, `version`, `ytt`
