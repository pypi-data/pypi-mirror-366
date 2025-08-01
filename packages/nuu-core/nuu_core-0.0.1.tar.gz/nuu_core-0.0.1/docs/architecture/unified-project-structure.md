# Unified Project Structure

## Project Layout

```
nuu-core/
├── .github/              # GitHub specific files
│   └── workflows/        # CI/CD workflows
├── docs/                 # Documentation
│   ├── architecture/     # Technical architecture docs
│   ├── prd/             # Product requirements
│   ├── stories/         # Development stories
│   └── epics/           # Epic definitions
├── nuu/                 # Main package directory
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # CLI entry point
│   ├── cli.py           # CLI command definitions
│   ├── fetch.py         # Core fetch logic
│   ├── parser.py        # Link parsing utilities
│   └── clipboard.py     # Clipboard operations
├── tests/               # Test directory
│   ├── __init__.py
│   ├── test_fetch.py
│   ├── test_parser.py
│   └── fixtures/        # Test markdown files
├── .gitignore          # Git ignore patterns
├── LICENSE             # MIT License
├── README.md           # Project documentation
├── pyproject.toml      # Project configuration
└── uv.lock            # Dependency lock file
```

## File Naming Conventions

### Python Files
- Use snake_case for all Python files
- Test files prefix with `test_`
- Private modules prefix with `_`

### Documentation
- Use kebab-case for markdown files
- Epic files: `epic-NNN-title.md`
- Story files: `N.N.story.md`

### Key Files

| File | Purpose |
|------|---------|
| `nuu/cli.py` | Typer app definition and commands |
| `nuu/fetch.py` | Core fetch logic and file resolution |
| `nuu/parser.py` | Wiki link extraction and parsing |
| `nuu/clipboard.py` | Cross-platform clipboard wrapper |

## Import Structure

```python
# External imports first
import typer
from pathlib import Path

# Internal imports
from nuu.fetch import fetch_document
from nuu.parser import extract_wiki_links
```