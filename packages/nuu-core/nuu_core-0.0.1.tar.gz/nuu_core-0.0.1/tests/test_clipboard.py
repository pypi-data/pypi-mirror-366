"""Tests for clipboard operations."""

import pytest
from unittest.mock import patch, MagicMock
from core.clipboard import copy_to_clipboard, count_words


class TestCopyToClipboard:
    """Test copy_to_clipboard function."""
    
    @patch('pyperclip.copy')
    def test_successful_copy(self, mock_copy):
        """Test successful clipboard copy."""
        content = "This is test content with several words"
        success, message = copy_to_clipboard(content)
        
        assert success is True
        assert "✓ Copied to clipboard" in message
        assert "(7 words)" in message
        mock_copy.assert_called_once_with(content)
    
    @patch('pyperclip.copy')
    def test_copy_with_large_content(self, mock_copy):
        """Test copying large content shows proper word count."""
        # Create content with 1500 words
        content = " ".join(["word"] * 1500)
        success, message = copy_to_clipboard(content)
        
        assert success is True
        assert "✓ Copied to clipboard" in message
        assert "(1,500 words)" in message  # Check comma formatting
        mock_copy.assert_called_once_with(content)
    
    @patch('pyperclip.copy')
    def test_copy_failure(self, mock_copy):
        """Test handling clipboard copy failure."""
        mock_copy.side_effect = Exception("Clipboard not available")
        
        content = "Test content"
        success, message = copy_to_clipboard(content)
        
        assert success is False
        assert "Failed to copy to clipboard" in message
        assert "Clipboard not available" in message
    
    @patch('pyperclip.copy')
    def test_empty_content(self, mock_copy):
        """Test copying empty content."""
        content = ""
        success, message = copy_to_clipboard(content)
        
        assert success is True
        assert "(0 words)" in message
        mock_copy.assert_called_once_with(content)


class TestCountWords:
    """Test count_words function."""
    
    def test_count_words_simple(self):
        """Test counting words in simple text."""
        assert count_words("Hello world") == 2
        assert count_words("This is a test") == 4
        assert count_words("Single") == 1
    
    def test_count_words_empty(self):
        """Test counting words in empty string."""
        assert count_words("") == 0
        assert count_words("   ") == 0
    
    def test_count_words_multiline(self):
        """Test counting words across multiple lines."""
        content = """First line
        Second line
        Third line"""
        assert count_words(content) == 6
    
    def test_count_words_with_punctuation(self):
        """Test that punctuation doesn't affect word count."""
        assert count_words("Hello, world!") == 2
        assert count_words("One. Two. Three.") == 3
        assert count_words("Hyphenated-word counts as one") == 4