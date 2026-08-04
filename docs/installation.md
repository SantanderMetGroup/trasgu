# Environment setup

## Install a release

For an isolated command-line installation, the recommended option is:

```bash
uv tool install trasgu
```

Trasgu is distributed as a standard Python package and does not require `uv`
at runtime. Installation with `pip` is also supported:

```bash
python -m pip install trasgu
```

Install the optional SLURM support with `trasgu[slurm]`, for example:

```bash
uv tool install "trasgu[slurm]"
```

## Install from a source checkout

Install the locked runtime environment with `uv`:

```bash
uv sync --frozen --no-dev
```

If `uv` is not installed yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

## Development environment

Install development tools:

```bash
uv sync --frozen
```

## SLURM support

The SLURM executor plugin is optional:

```bash
uv sync --frozen --extra slurm
```

Use this on clusters where you plan to run:

```bash
trasgu_run --profile slurm
```

`uv` is the supported tool for maintaining the repository: dependency locking,
development environments, tests, builds, and releases all use it. This does
not restrict how an installed Trasgu package is run or which standards-compliant
Python installer downstream users choose.
