"""Test that dependencies are properly installed."""
import sys


def test_typer_installed():
    """Test that typer is installed."""
    import typer
    assert typer.__version__


def test_pyperclip_installed():
    """Test that pyperclip is installed."""
    import pyperclip
    assert hasattr(pyperclip, 'copy')
    assert hasattr(pyperclip, 'paste')


def test_pyyaml_installed():
    """Test that pyyaml is installed."""
    import yaml
    assert hasattr(yaml, 'safe_load')


def test_python_version():
    """Test that Python version meets requirements."""
    assert sys.version_info >= (3, 11)