# Development

## Install development tools

```bash
uv sync --frozen
```

## Run tests

```bash
uv run pytest
```

## Run linting

```bash
uv run ruff check .
```

## CLI help tests

The test suite checks that every public CLI command supports `--help` and documents the expected run-directory behavior.

When adding a new entrypoint in `pyproject.toml`, add it to the CLI help tests and to [CLI reference](cli-reference.md).

## Documentation

Documentation source files live in `docs/` and are configured by `mkdocs.yml`.

Serve locally:

```bash
uvx --with mkdocs-material mkdocs serve
```

Build locally:

```bash
uvx --with mkdocs-material mkdocs build --strict
```
