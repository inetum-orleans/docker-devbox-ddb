## Build and release process


```
prerelease

rm -Rf dist/ &&\
python setup.py clean build bdist bdist_wheel bdist_pex --pex-args="--disable-cache" --bdist-all &&\
docker run --rm --init -v "$(pwd):/src/" cdrx/pyinstaller-linux:xenial "pyinstaller --clean -y --dist ./dist --workpath /tmp *.spec"

release

githubrelease release gfi-centre-ouest/docker-devbox-ddb create $(python -m ddb --version | cut -d ' ' -f 3-) --publish "dist/*"

postrelease
```

## Windows json

In progress ...
