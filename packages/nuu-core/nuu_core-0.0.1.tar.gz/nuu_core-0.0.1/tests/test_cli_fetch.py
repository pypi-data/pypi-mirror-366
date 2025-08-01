"""Tests for CLI fetch command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.cli import app
from core.fetch import DocumentNotFoundError


runner = CliRunner()


class TestFetchCommand:
    """Test the fetch CLI command."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_content = """# Test Document
[Source: /test/path.md]

Test content here."""
        self.warnings = []
    
    @patch('core.cli.fetch_document')
    @patch('core.cli.copy_to_clipboard')
    def test_fetch_success(self, mock_copy, mock_fetch):
        """Test successful fetch with clipboard copy."""
        mock_fetch.return_value = (self.test_content, self.warnings)
        mock_copy.return_value = (True, "✓ Copied to clipboard (4 words)")
        
        result = runner.invoke(app, ["fetch", "Test Document"])
        
        assert result.exit_code == 0
        assert "✓ Copied to clipboard (4 words)" in result.stdout
        mock_fetch.assert_called_once_with("Test Document", depth=1)
        mock_copy.assert_called_once_with(self.test_content)
    
    @patch('core.cli.fetch_document')
    def test_fetch_with_no_copy(self, mock_fetch):
        """Test fetch with --no-copy outputs to stdout."""
        mock_fetch.return_value = (self.test_content, self.warnings)
        
        result = runner.invoke(app, ["fetch", "Test Document", "--no-copy"])
        
        assert result.exit_code == 0
        assert self.test_content in result.stdout
        mock_fetch.assert_called_once_with("Test Document", depth=1)
    
    @patch('core.cli.fetch_document')
    def test_fetch_with_warnings(self, mock_fetch):
        """Test fetch displays warnings."""
        warnings = ["Could not find linked document 'Missing'"]
        mock_fetch.return_value = (self.test_content, warnings)
        
        result = runner.invoke(app, ["fetch", "Test Document", "--no-copy"])
        
        assert result.exit_code == 0
        assert "Warning: Could not find linked document 'Missing'" in result.stderr
        assert self.test_content in result.stdout
    
    @patch('core.cli.fetch_document')
    def test_fetch_document_not_found(self, mock_fetch):
        """Test error when document not found."""
        mock_fetch.side_effect = DocumentNotFoundError("Document 'Missing' not found in vault")
        
        result = runner.invoke(app, ["fetch", "Missing"])
        
        assert result.exit_code == 1
        assert "Error: Document 'Missing' not found in vault" in result.stderr
    
    @patch('core.cli.fetch_document')
    def test_fetch_invalid_depth(self, mock_fetch):
        """Test error with invalid depth."""
        mock_fetch.side_effect = ValueError("Only depth=1 is supported in MVP")
        
        result = runner.invoke(app, ["fetch", "Test", "--depth", "2"])
        
        assert result.exit_code == 1
        assert "Error: Only depth=1 is supported in MVP" in result.stderr
    
    @patch('core.cli.fetch_document')
    @patch('core.cli.copy_to_clipboard')
    def test_fetch_clipboard_failure_fallback(self, mock_copy, mock_fetch):
        """Test fallback to stdout when clipboard fails."""
        mock_fetch.return_value = (self.test_content, self.warnings)
        mock_copy.return_value = (False, "Failed to copy to clipboard: No clipboard available")
        
        result = runner.invoke(app, ["fetch", "Test Document"])
        
        assert result.exit_code == 0
        assert "Warning: Failed to copy to clipboard" in result.stderr
        assert "Outputting to stdout instead:" in result.stderr
        assert self.test_content in result.stdout
    
    @pytest.mark.skip(reason="Typer 0.12.5 has compatibility issues with help")
    def test_fetch_help(self):
        """Test fetch command help."""
        result = runner.invoke(app, ["fetch", "--help"])
        
        assert result.exit_code == 0
        assert "Fetch a markdown file and its linked documents" in result.stdout
        assert "--depth" in result.stdout
        assert "--no-copy" in result.stdout