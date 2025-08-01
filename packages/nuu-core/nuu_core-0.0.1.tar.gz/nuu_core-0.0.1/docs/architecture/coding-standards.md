# Coding Standards

## Python Style Guide

### General Principles
- Follow PEP 8 with 120 character line limit
- Use type hints for all function signatures
- Prefer explicit over implicit
- Keep functions small and focused

### Type Hints
```python
from pathlib import Path
from typing import Optional, List

def fetch_document(
    file_identifier: str,
    vault_path: Path = Path("."),
    depth: int = 1
) -> Optional[str]:
    """Fetch a document and its linked content."""
    ...
```

### Error Handling
- Use custom exceptions for domain errors
- Let typer handle CLI errors
- Always provide helpful error messages

```python
class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found."""
    pass
```

### Documentation
- All public functions must have docstrings
- Use Google-style docstrings
- Include type information in docstrings

```python
def extract_wiki_links(content: str) -> List[str]:
    """Extract wiki-style links from markdown content.
    
    Args:
        content: The markdown content to parse
        
    Returns:
        List of link targets (without brackets)
        
    Example:
        >>> extract_wiki_links("See [[Example]] for more")
        ['Example']
    """
```

### Testing Standards
- Minimum 80% code coverage
- Test edge cases and error conditions
- Use pytest fixtures for test data
- Keep tests independent and fast

### CLI Standards
- Use typer decorators for commands
- Provide helpful descriptions
- Show progress for long operations
- Always confirm destructive operations

```python
@app.command()
def fetch(
    file: str = typer.Argument(..., help="File name or path to fetch"),
    depth: int = typer.Option(1, "--depth", "-d", help="Link traversal depth"),
    no_copy: bool = typer.Option(False, "--no-copy", help="Output to stdout instead of clipboard"),
):
    """Fetch a markdown file and its linked documents."""
    ...
```