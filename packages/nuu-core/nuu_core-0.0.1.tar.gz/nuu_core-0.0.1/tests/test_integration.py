"""Integration tests for the full fetch workflow."""

import pytest
from pathlib import Path
from core.fetch import fetch_document, DocumentNotFoundError
from core.parser import extract_wiki_links


class TestIntegration:
    """Test the complete fetch workflow with real files."""
    
    @pytest.fixture
    def fixtures_path(self):
        """Get path to test fixtures."""
        return Path(__file__).parent / "fixtures"
    
    def test_fetch_simple_document(self, fixtures_path):
        """Test fetching a simple document with no links."""
        content, warnings = fetch_document("simple", vault_path=fixtures_path)
        
        assert "# Simple Document" in content
        assert "This is a simple document with no wiki links" in content
        assert "Linked Documents" not in content
        assert warnings == []
    
    def test_fetch_document_with_links(self, fixtures_path):
        """Test fetching a document with multiple wiki links."""
        content, warnings = fetch_document("with_links", vault_path=fixtures_path)
        
        # Check main document
        assert "# Document with Links" in content
        assert "This document references [[Link1]]" in content
        
        # Check linked documents section
        assert "## Linked Documents (Depth 1)" in content
        assert "### [[Link1]]" in content
        assert "This is the content of Link1" in content
        assert "### [[Link2|Different Display Name]]" in content
        assert "This is the content of Link2" in content
        
        # Should have no warnings
        assert warnings == []
        
        # Check that Link1 appears only once despite multiple references (including section ref)
        assert content.count("This is the content of Link1") == 1
        # Link1#Section should not create a separate entry since it's the same file
        assert content.count("### [[Link1#Section]]") == 0
    
    def test_fetch_with_broken_links(self, fixtures_path):
        """Test fetching with references to missing documents."""
        content, warnings = fetch_document("broken_links", vault_path=fixtures_path)
        
        # Should have main content
        assert "# Document with Broken Links" in content
        
        # Should have existing link
        assert "### [[Exists]]" in content
        assert "This document exists and can be referenced" in content
        
        # Should have warnings for missing links
        assert len(warnings) == 2
        assert any("Missing Document" in w for w in warnings)
        assert any("Another Missing" in w for w in warnings)
    
    def test_parser_with_fixtures(self, fixtures_path):
        """Test parser on real fixture files."""
        # Test simple document
        simple_path = fixtures_path / "simple.md"
        simple_content = simple_path.read_text()
        assert extract_wiki_links(simple_content) == []
        
        # Test document with links
        links_path = fixtures_path / "with_links.md"
        links_content = links_path.read_text()
        links = extract_wiki_links(links_content)
        assert "Link1" in links
        assert "Link2" in links
        assert "Link1#Section" in links
        assert len(links) == 3  # No duplicates
    
    def test_case_insensitive_search(self, fixtures_path):
        """Test case-insensitive file search."""
        # Should find files regardless of case
        content1, _ = fetch_document("SIMPLE", vault_path=fixtures_path)
        content2, _ = fetch_document("Simple", vault_path=fixtures_path)
        content3, _ = fetch_document("simple", vault_path=fixtures_path)
        
        # All should have same content
        assert "# Simple Document" in content1
        assert content1 == content2 == content3
    
    def test_document_not_found(self, fixtures_path):
        """Test error handling for non-existent documents."""
        with pytest.raises(DocumentNotFoundError) as exc_info:
            fetch_document("NonExistent", vault_path=fixtures_path)
        
        assert "Document 'NonExistent' not found" in str(exc_info.value)