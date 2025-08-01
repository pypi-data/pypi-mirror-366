"""Tests for wiki link parser."""

import pytest
from core.parser import extract_wiki_links


class TestExtractWikiLinks:
    """Test extract_wiki_links function."""
    
    def test_simple_links(self):
        """Test extraction of simple wiki links."""
        content = "This is a [[Simple Link]] and another [[Test Link]]."
        links = extract_wiki_links(content)
        assert links == ["Simple Link", "Test Link"]
    
    def test_links_with_aliases(self):
        """Test extraction of links with display aliases."""
        content = "See [[Original Title|Display Name]] for details."
        links = extract_wiki_links(content)
        assert links == ["Original Title"]
    
    def test_links_with_sections(self):
        """Test extraction of links with section anchors."""
        content = "Refer to [[Document#Section]] and [[Page#Introduction]]."
        links = extract_wiki_links(content)
        assert links == ["Document#Section", "Page#Introduction"]
    
    def test_mixed_link_formats(self):
        """Test extraction with mixed link formats."""
        content = """
        # Document with various links
        
        - [[Simple Link]]
        - [[Document Title|Short Name]]
        - [[Page#Specific Section]]
        - [[Complex Title|Alias#With Section]] 
        """
        links = extract_wiki_links(content)
        assert links == [
            "Simple Link",
            "Document Title",
            "Page#Specific Section",
            "Complex Title"
        ]
    
    def test_duplicate_links(self):
        """Test that duplicate links are not included."""
        content = "[[Same Link]] and again [[Same Link]] plus [[Same Link]]"
        links = extract_wiki_links(content)
        assert links == ["Same Link"]
    
    def test_no_links(self):
        """Test content with no wiki links."""
        content = "This document has no wiki links at all."
        links = extract_wiki_links(content)
        assert links == []
    
    def test_empty_links(self):
        """Test handling of empty or whitespace-only links."""
        content = "[[]] and [[   ]] should be ignored"
        links = extract_wiki_links(content)
        assert links == []
    
    def test_nested_brackets(self):
        """Test links with nested brackets are not matched."""
        content = "This [[valid link]] but [[[not valid]]] and [[[[also not]]]]"
        links = extract_wiki_links(content)
        assert links == ["valid link"]
    
    def test_multiline_content(self):
        """Test extraction across multiple lines."""
        content = """
        # Main Document
        
        This references [[First Document]] in the introduction.
        
        ## Section 1
        See also [[Second Document|Reference]] for more details.
        
        ## Section 2
        Finally check [[Third Document#Conclusion]].
        """
        links = extract_wiki_links(content)
        assert links == [
            "First Document",
            "Second Document",
            "Third Document#Conclusion"
        ]
    
    def test_special_characters_in_links(self):
        """Test links containing special characters."""
        content = """
        - [[File-with-dashes]]
        - [[File_with_underscores]]
        - [[File with spaces]]
        - [[2024-01-15 Daily Note]]
        """
        links = extract_wiki_links(content)
        assert links == [
            "File-with-dashes",
            "File_with_underscores",
            "File with spaces",
            "2024-01-15 Daily Note"
        ]