"""Test basic package structure."""
import core


def test_version():
    """Test that version is properly defined."""
    assert core.__version__ == "0.1.0"
    

def test_package_has_docstring():
    """Test that package has a docstring."""
    assert core.__doc__ is not None
    assert "CLI tool" in core.__doc__