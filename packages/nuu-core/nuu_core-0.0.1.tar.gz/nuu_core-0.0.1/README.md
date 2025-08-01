# Core

A CLI tool for fetching markdown content with linked documents.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/core.git
cd core

# Install using uv (recommended)
uv sync

# Or install using pip
pip install -e .
```

## Usage

### Check Version

```bash
core version
# or
core --version
```

### Run as Module

```bash
python -m core version
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run pyright
```

### Project Structure

```
core/
├── src/
│   └── core/         # Main package
│       ├── __init__.py   # Package initialization
│       ├── __main__.py   # Module entry point
│       └── cli.py        # CLI commands
├── tests/            # Test suite
├── docs/             # Documentation
└── pyproject.toml    # Project configuration
```

## Requirements

- Python 3.11 or higher
- uv (recommended) or pip

## License

MIT License - see LICENSE file for details.
