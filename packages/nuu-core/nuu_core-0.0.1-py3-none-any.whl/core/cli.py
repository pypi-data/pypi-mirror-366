"""Main CLI application for Core."""
import typer
from typing import Optional

from core import __version__
from core.fetch import fetch_document, DocumentNotFoundError
from core.clipboard import copy_to_clipboard

def version_callback(value: bool):
    """Handle version flag."""
    if value:
        print(f"core version {__version__}")
        raise typer.Exit()


app = typer.Typer()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the core version"
    ),
):
    """A CLI tool for fetching markdown content with linked documents."""
    pass


@app.command()
def version():
    """Show the core version."""
    print(f"core version {__version__}")


@app.command()
def fetch(
    file: str = typer.Argument(..., help="File name or path to fetch"),
    depth: int = typer.Option(1, "--depth", "-d", help="Link traversal depth"),
    no_copy: bool = typer.Option(False, "--no-copy", help="Output to stdout instead of clipboard"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Tag suffix for linked documents"),
):
    """Fetch a markdown file and its linked documents."""
    try:
        # Fetch the document and linked content
        content, warnings = fetch_document(file, depth=depth, tag=tag)
        
        # Display any warnings
        for warning in warnings:
            typer.echo(f"Warning: {warning}", err=True)
        
        if no_copy:
            # Output to stdout
            typer.echo(content)
        else:
            # Copy to clipboard
            success, message = copy_to_clipboard(content)
            if success:
                typer.echo(message)
            else:
                # Fall back to stdout with warning
                typer.echo(f"Warning: {message}", err=True)
                typer.echo("Outputting to stdout instead:", err=True)
                typer.echo(content)
                
    except DocumentNotFoundError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()