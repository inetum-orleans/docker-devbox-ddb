doc-watch:
	docker run --rm -it -p 8000:8000 --user $(id -u):$(id -g) -v ${PWD}:/docs squidfunk/mkdocs-material serve

doc-publish:
	docker run --rm -it -p 8000:8000 --user $(id -u):$(id -g) -v ${PWD}/..:/docs -v ${HOME}/.netrc:/.netrc:ro --workdir=/docs/ddb squidfunk/mkdocs-material gh-deploy

git-pre-push:
	make style
	make test

style:
	uv run pre-commit run --all-files

test:
	uv run pytest

binary:
	uv run pyinstaller --dist ./dist ddb.spec
