"""Clipboard operations wrapper."""

import pyperclip
from typing import Tuple


def copy_to_clipboard(content: str) -> Tuple[bool, str]:
    """Copy content to system clipboard.
    
    Args:
        content: Text content to copy to clipboard
        
    Returns:
        Tuple of (success, message)
    """
    try:
        pyperclip.copy(content)
        word_count = len(content.split())
        return True, f"✓ Copied to clipboard ({word_count:,} words)"
    except Exception as e:
        return False, f"Failed to copy to clipboard: {str(e)}"


def count_words(content: str) -> int:
    """Count words in content.
    
    Args:
        content: Text content to count words in
        
    Returns:
        Number of words
    """
    return len(content.split())