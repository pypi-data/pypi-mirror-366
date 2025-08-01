"""Test that project files exist and are valid."""
from pathlib import Path


def test_readme_exists():
    """Test that README.md exists and has content."""
    readme = Path("README.md")
    assert readme.exists()
    content = readme.read_text()
    assert "Core" in content
    assert "Installation" in content
    assert "Usage" in content


def test_license_exists():
    """Test that LICENSE file exists."""
    license_file = Path("LICENSE")
    assert license_file.exists()
    content = license_file.read_text()
    assert "MIT License" in content


def test_gitignore_exists():
    """Test that .gitignore exists and has Python entries."""
    gitignore = Path(".gitignore")
    assert gitignore.exists()
    content = gitignore.read_text()
    assert "__pycache__/" in content
    assert ".venv" in content
    assert "*.py[cod]" in content


def test_docs_directory_exists():
    """Test that docs directory structure exists."""
    docs_dir = Path("docs")
    assert docs_dir.exists()
    assert docs_dir.is_dir()
    
    # Check subdirectories
    assert (docs_dir / "stories").exists()
    assert (docs_dir / "architecture").exists()
    assert (docs_dir / "prd").exists()