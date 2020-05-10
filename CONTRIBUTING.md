## Build and release process

The release process requires docker with custom images of `cdrx/pyinstaller-linux` and `cdrx/pyinstaller-windows` that 
should be build from [Toilal/docker-pyinstaller#more-variations](https://github.com/Toilal/docker-pyinstaller/tree/more-variations) with `build.sh` script.

A [pull request is opened](https://github.com/cdrx/docker-pyinstaller/pull/90) and I hope it will be merged and available on docker hub soon.

```
prerelease

rm -Rf dist/ &&\
python setup.py clean build bdist bdist_wheel bdist_pex --pex-args="--disable-cache" --bdist-all &&\
docker run --rm --init -v "$(pwd):/src/" -e "DISABLE_REQUIREMENTS=1" cdrx/pyinstaller-linux:xenial "pip install --upgrade setuptools && pip install -r requirements.txt && pyinstaller --clean -y --dist ./dist --workpath /tmp *.spec" &&\
docker run --rm --init -v "$(pwd):/src/" -e "DISABLE_REQUIREMENTS=1" cdrx/pyinstaller-windows "pip install --upgrade setuptools && pip install whl/jsonnet-0.15.0-cp37-cp37m-win_amd64.whl && pip install -r requirements.txt && pyinstaller --clean -y --dist ./dist --workpath /tmp *.spec"

release

githubrelease release gfi-centre-ouest/docker-devbox-ddb create $(python -m ddb --version -s) --publish "dist/*"

postrelease
```
