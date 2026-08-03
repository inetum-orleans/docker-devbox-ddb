# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**ddb** (`docker-devbox-ddb` on PyPI) is a CLI tool that generates and adjusts configuration files from a single
overridable configuration, primarily for docker compose projects. It is distributed both as a Python package and as
standalone binaries (PyInstaller). User documentation lives in `docs/` and is published with mkdocs-material.

## Development commands

Dependencies, virtualenv and interpreters are managed by [uv](https://docs.astral.sh/uv/); everything runs through
`uv run`, so the versions used are the ones locked in `uv.lock`.

```bash
uv sync                        # create .venv from uv.lock (dev group)
uv run pytest                  # run the whole test suite
uv run pytest -m "not docker"  # skip tests that need a docker engine
uv run pytest --cov=ddb        # with coverage (what CI runs)
uv run pytest tests/feature/gitignore/test_gitignore.py::TestUpdateGitIgnoreAction::test_empty_project_with_core  # single test
uv run ruff check              # lint, blocking in CI
uv run ruff format             # format
uv run pre-commit run --all-files   # the full quality gate, as CI runs it
uv run tox                     # run the suite on py311..py314
uv run pyinstaller --dist ./dist ddb.spec  # build the standalone binary
make doc-watch                 # serve docs on http://localhost:8000 via docker
```

The [ytt](https://carvel.dev/ytt/) binary must be in `PATH` for the ytt feature tests to pass. On Windows, run the CLI
with `python -m ddb` instead of `ddb`.

Supported interpreters are 3.11 → 3.14. `ddb/utils/simpleeval.py`, `ddb/feature/docker/lib` and
`pytest_docker_compose` are vendored copies excluded from ruff, so leave their formatting alone.

Commits must follow [conventional commits](https://www.conventionalcommits.org/) — commitizen (`uv run cz check`)
rejects invalid messages in CI, and `uv run cz commit` helps write them. `ddb/__version__.py` is bumped by
python-semantic-release on push to `master`; never edit the version by hand. Day-to-day work happens on `develop`.

Integration tests spin up a cfssl container. If a run is interrupted, leftover `*-cfssl-1` containers make later runs
fail with `ContainersAlreadyExist` — remove them before re-running.

## Architecture

### Registries and the main flow

Everything is wired through global registries (`ddb/registry.py`): `features`, `phases`, `commands`, `actions`,
`binaries`, `services`, `caches`. `ddb/__main__.py:main()` orchestrates the whole run:

1. `load_plugins()` — imports `Feature` subclasses from any `.ddb` directory found in the config paths.
2. `bootstrap_register_features()` — resolves features (defaults + `ddb_features` setuptools entry points + plugins)
   and registers them in dependency order (topological sort of `Feature.dependencies`, `ddb/feature/bootstrap.py`).
3. `preload_registered_features()` — registers phases and commands so argparse can build the CLI.
4. `parse_command_line()` — global flags plus one subparser per registered command.
5. `load_registered_features()` — validates each feature's configuration against its marshmallow schema, then registers
   actions, binaries and services.
6. `register_actions_in_event_bus()` — binds every action's `event_bindings` to the bus, sorted by `Action.order`.
7. The command executes its phases; each phase emits `phase:<name>` on the bus, which triggers the bound actions.

**Feature registration order matters**: within a phase, actions of equal `order` run in the order their features were
registered, which is the topological order of dependencies.

### Event-driven actions

`ddb/event/bus.py` is a synchronous global bus; event names are declared as decorated methods in `ddb/event/events.py`
(e.g. `events.file.found` → `"file:found"`). An `Action` declares `event_bindings`, either an event name/callable or an
`EventBinding(event, call=..., processor=...)`. The `processor` runs before the action: returning `None`/`False` skips
it, returning a `(args, kwargs)` tuple remaps the call. Actions raise further events, so features chain reactively.

- `InitializableAction` gets a lazy `initialize()` before its first execution and a `destroy()` on config reload.
- `WatchSupport` actions are started when `-w/--watch` is passed.
- Exceptions are collected in `context.exceptions` and logged; `-ff/--fail-fast` (or a `FailFastError`) aborts instead
  (`ddb/action/runner.py`).

### Template generation pipeline

This is the core of `ddb configure`. The `file` feature walks the project and emits `file:found` per file. Template
features (`jinja`, `jsonnet`, `ytt`, `symlinks`, `copy`) extend `AbstractTemplateAction` (`ddb/action/action.py`) and
use a `TemplateFinder` (`ddb/utils/file.py`) to map a source to a target by stripping a configured suffix
(`.jinja`, `.jsonnet`, `.ytt`, …). The rendered content is written only if it differs, then `file:generated` is emitted,
which re-enters the pipeline — this is how chained templates (`docker-compose.yml.jsonnet.jinja`) work, and how the
`gitignore` feature learns which generated files to ignore. Rendered output is cached per target so a deleted template
only removes its target when the target was left untouched.

### Configuration

`ddb/config/config.py` holds a `Dotty` dict merged (deepmerge, `ddb/config/merger.py`) from `ddb.yml`/`ddb.local.yml`
found in four paths: `ddb_home`, `home`, `user_home`, `project_home` (project home is discovered by walking up from
cwd). `core` inserts the environment file `ddb.<env>.yml` by raising `ConfigureSecondPassException`, which restarts the
configuration pass. Any value can be overridden by an environment variable named after its path
(`DDB_OVERRIDE_CORE_DOMAIN_EXT`). `ddb/config/migrations.py` renames legacy configuration keys transparently.

Each feature validates its own configuration section (keyed by feature name) with a marshmallow schema in
`schema.py`; `_configure_defaults()` is where context-dependent defaults are computed (e.g. docker host IP,
project name from the directory).

### Adding a feature

Create `ddb/feature/<name>/` with `__init__.py` (the `Feature` subclass), `actions.py` and `schema.py`, add the
instance to `_default_available_features` in `ddb/feature/bootstrap.py`, add `docs/features/<name>.md` and its
`mkdocs.yml` nav entry, and create `tests/feature/<name>/`. External features can instead be shipped as a
`ddb_features` entry point or dropped into a project's `.ddb` directory.

## Tests

- The `project_loader` fixture (`tests/conftest.py`) copies a fixture project from `<test_module>.data/<name>` into a
  temp directory and chdirs into it, so tests run against a real filesystem.
- Unit-style tests register the features they need (`features.register(...)` + `load_registered_features()`) and call
  actions directly; integration tests in `tests/it/` call `main([...])` from `ddb.__main__` with CLI arguments.
- An autouse fixture resets all registries, config and environment between tests, and forces `fail_fast` on.
- `@pytest.mark.docker` marks tests requiring a docker engine; `docker-compose.yml` at the repo root provides the cfssl
  container used by certs tests, driven by the vendored fork in `pytest_docker_compose/`.

## Code conventions

- `ruff check` and `ruff format` must pass; the rule set, the 120-column limit and the justified per-file exceptions
  live in `pyproject.toml`. Docstrings on classes, functions and methods remain the house style.
- Code must remain compatible with Python 3.11 (CI matrix is 3.11 → 3.14).
- Cross-platform behaviour (Linux, Windows, macOS/alpine binaries) is expected; prefer helpers from `ddb/utils/`
  (`file.py`, `process.py`, `compat.py`) over raw `os`/`subprocess` calls where one exists.
