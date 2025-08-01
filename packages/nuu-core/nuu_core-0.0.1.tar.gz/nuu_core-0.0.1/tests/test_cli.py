"""Test CLI functionality."""
import subprocess
from typer.testing import CliRunner
from core.cli import app


runner = CliRunner()


def test_version_command():
    """Test the version command works."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "core version 0.1.0" in result.stdout


def test_version_flag():
    """Test the --version flag works."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "core version 0.1.0" in result.stdout


def test_cli_entry_point():
    """Test that the CLI can be run via entry point."""
    result = subprocess.run(
        ["uv", "run", "core", "version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "core version 0.1.0" in result.stdout


def test_module_execution():
    """Test that the CLI can be run as a module."""
    result = subprocess.run(
        ["uv", "run", "python", "-m", "core", "version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "core version 0.1.0" in result.stdout