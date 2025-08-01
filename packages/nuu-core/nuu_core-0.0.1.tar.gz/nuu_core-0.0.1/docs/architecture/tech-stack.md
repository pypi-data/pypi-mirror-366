# Technology Stack

## Programming Language
- **Python 3.11+**: Modern Python with type hints
- **Rationale**: Fast development, excellent CLI libraries, cross-platform

## Core Dependencies
- **typer**: Modern CLI framework built on Click
  - Type hints for argument parsing
  - Automatic help generation
  - Clean, declarative syntax
  
- **pyperclip**: Cross-platform clipboard operations
  - Works on macOS, Linux, Windows
  - Simple API
  
- **pyyaml**: YAML parsing for future config support
  - Standard in Python ecosystem
  - Human-readable configuration

## Development Tools
- **uv**: Modern Python package manager
  - Fast, Rust-based
  - Deterministic dependency resolution
  - Built-in Python version management
  
- **ruff**: Linting and formatting
  - Fast, comprehensive
  - Replaces black, isort, flake8
  
- **pyright**: Type checking
  - Strict type validation
  - IDE integration

## Testing
- **pytest**: Testing framework
  - Industry standard
  - Rich plugin ecosystem
  - Good async support

## Distribution
- **pyproject.toml**: Modern Python packaging
- **PyPI**: Standard distribution channel
- **GitHub Releases**: Binary distributions (future)