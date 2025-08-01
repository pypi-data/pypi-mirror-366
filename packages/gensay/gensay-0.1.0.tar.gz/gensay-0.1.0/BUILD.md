# Building gensay with uv

This project is configured to work with [uv](https://github.com/astral-sh/uv) for dependency management and building.

## Installation

```bash
# Install the project in development mode
uv pip install -e .

# Install with all optional dependencies
uv pip install -e ".[all]"

# Install with specific extras
uv pip install -e ".[openai,audio-formats]"
```

## Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Or use uv sync to install from lock file
uv sync --dev
```

## Building

```bash
# Build the package
uv build

# Build without including local source references
uv build --no-sources

# Build a specific package format
uv build --sdist  # Source distribution only
uv build --wheel  # Wheel only
```

## Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=gensay --cov-report=term-missing

# Run type checking
uv run mypy src/gensay tests

# Run linting
uv run ruff check --fix
uv run ruff format
```

## Publishing

```bash
# Build for publishing (without local sources)
uv build --no-sources

# Upload to PyPI (requires API token)
uv publish

# Or use twine
uv run twine upload dist/*
```

## Managing Dependencies

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest-mock

# Update dependencies
uv sync

# Show dependency tree
uv tree
```