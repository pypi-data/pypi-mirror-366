"""Tests for document fetching and file resolution."""

import pytest
from pathlib import Path
from core.fetch import find_markdown_file, fetch_document, compile_content, DocumentNotFoundError


class TestFindMarkdownFile:
    """Test find_markdown_file function."""
    
    def test_find_existing_file(self, tmp_path):
        """Test finding an existing markdown file."""
        # Create test file
        test_file = tmp_path / "Test Document.md"
        test_file.write_text("# Test Document\nContent here")
        
        # Find by exact title
        result = find_markdown_file("Test Document", tmp_path)
        assert result == test_file
    
    def test_find_case_insensitive(self, tmp_path):
        """Test case-insensitive file matching."""
        # Create test file
        test_file = tmp_path / "Test Document.md"
        test_file.write_text("# Test Document")
        
        # Find with different cases
        assert find_markdown_file("test document", tmp_path) == test_file
        assert find_markdown_file("TEST DOCUMENT", tmp_path) == test_file
        assert find_markdown_file("Test DOCUMENT", tmp_path) == test_file
    
    def test_find_in_subdirectory(self, tmp_path):
        """Test finding files in subdirectories."""
        # Create subdirectory with file
        subdir = tmp_path / "notes"
        subdir.mkdir()
        test_file = subdir / "Meeting Notes.md"
        test_file.write_text("# Meeting Notes")
        
        # Should find file in subdirectory
        result = find_markdown_file("Meeting Notes", tmp_path)
        assert result == test_file
    
    def test_file_not_found(self, tmp_path):
        """Test error when file not found."""
        with pytest.raises(DocumentNotFoundError) as exc_info:
            find_markdown_file("Nonexistent", tmp_path)
        
        assert "Document 'Nonexistent' not found in vault" in str(exc_info.value)
    
    def test_multiple_files_same_name(self, tmp_path):
        """Test behavior with multiple files having same title."""
        # Create two files with same title in different directories
        file1 = tmp_path / "Document.md"
        file1.write_text("First")
        
        subdir = tmp_path / "archive"
        subdir.mkdir()
        file2 = subdir / "Document.md"
        file2.write_text("Second")
        
        # Should find one of them (first encountered)
        result = find_markdown_file("Document", tmp_path)
        assert result in [file1, file2]


class TestFetchDocument:
    """Test fetch_document function."""
    
    def test_fetch_simple_document(self, tmp_path):
        """Test fetching a document with no links."""
        # Create test file
        doc = tmp_path / "Simple.md"
        doc.write_text("This is a simple document with no links.")
        
        content, warnings = fetch_document("Simple", vault_path=tmp_path)
        
        assert "# Simple" in content
        assert f"[Source: {doc}]" in content
        assert "This is a simple document with no links." in content
        assert warnings == []
        assert "Linked Documents" not in content
    
    def test_fetch_with_links(self, tmp_path):
        """Test fetching a document with wiki links."""
        # Create main document
        main = tmp_path / "Main.md"
        main.write_text("This references [[First]] and [[Second]].")
        
        # Create linked documents
        first = tmp_path / "First.md"
        first.write_text("Content of first document.")
        
        second = tmp_path / "Second.md"
        second.write_text("Content of second document.")
        
        content, warnings = fetch_document("Main", vault_path=tmp_path)
        
        # Check main content
        assert "# Main" in content
        assert f"[Source: {main}]" in content
        assert "This references [[First]] and [[Second]]." in content
        
        # Check linked documents section
        assert "## Linked Documents (Depth 1)" in content
        assert "### [[First]]" in content
        assert f"[Source: {first}]" in content
        assert "Content of first document." in content
        assert "### [[Second]]" in content
        assert f"[Source: {second}]" in content
        assert "Content of second document." in content
        
        assert warnings == []
    
    def test_fetch_with_missing_links(self, tmp_path):
        """Test fetching with links to missing documents."""
        # Create main document with broken link
        main = tmp_path / "Main.md"
        main.write_text("This references [[Exists]] and [[Missing]].")
        
        # Create only one linked document
        exists = tmp_path / "Exists.md"
        exists.write_text("This file exists.")
        
        content, warnings = fetch_document("Main", vault_path=tmp_path)
        
        # Should have main content
        assert "# Main" in content
        assert "This references [[Exists]] and [[Missing]]." in content
        
        # Should have existing linked document
        assert "### [[Exists]]" in content
        assert "This file exists." in content
        
        # Should have warning about missing document
        assert len(warnings) == 1
        assert "Could not find linked document 'Missing'" in warnings[0]
    
    def test_fetch_with_aliases(self, tmp_path):
        """Test fetching with aliased wiki links."""
        # Create main with aliased link
        main = tmp_path / "Main.md"
        main.write_text("See [[Document Title|Short Name]] for details.")
        
        # Create linked document
        doc = tmp_path / "Document Title.md"
        doc.write_text("Full document content.")
        
        content, warnings = fetch_document("Main", vault_path=tmp_path)
        
        # Should fetch the document using the actual title, not alias
        assert "### [[Document Title|Short Name]]" in content
        assert "Full document content." in content
        assert warnings == []
    
    def test_fetch_with_sections(self, tmp_path):
        """Test fetching with section links."""
        # Create main with section link
        main = tmp_path / "Main.md"
        main.write_text("See [[Document#Section]] for specific info.")
        
        # Create linked document
        doc = tmp_path / "Document.md"
        doc.write_text("Document with sections.")
        
        content, warnings = fetch_document("Main", vault_path=tmp_path)
        
        # Should fetch the document ignoring section reference
        assert "### [[Document#Section]]" in content
        assert "Document with sections." in content
        assert warnings == []
    
    def test_depth_validation(self, tmp_path):
        """Test that only depth=1 is supported."""
        doc = tmp_path / "Test.md"
        doc.write_text("Content")
        
        # depth=1 should work
        content, warnings = fetch_document("Test", depth=1, vault_path=tmp_path)
        assert "# Test" in content
        
        # Other depths should raise error
        with pytest.raises(ValueError) as exc_info:
            fetch_document("Test", depth=2, vault_path=tmp_path)
        assert "Only depth=1 is supported" in str(exc_info.value)
    
    def test_duplicate_links(self, tmp_path):
        """Test that duplicate links are not fetched multiple times."""
        # Create main with duplicate links
        main = tmp_path / "Main.md"
        main.write_text("First [[Doc]], then [[Doc]] again, and [[Doc]] once more.")
        
        # Create linked document
        doc = tmp_path / "Doc.md"
        doc.write_text("Document content.")
        
        content, warnings = fetch_document("Main", vault_path=tmp_path)
        
        # Should only include the document once
        assert content.count("### [[Doc]]") == 1
        assert content.count("Document content.") == 1
        assert warnings == []


class TestCompileContent:
    """Test compile_content function."""
    
    def test_compile_without_links(self, tmp_path):
        """Test compiling content with no linked documents."""
        main_path = tmp_path / "Test.md"
        main_content = "This is the main content."
        
        result = compile_content(main_path, main_content, [])
        
        assert result == f"""# Test
[Source: {main_path}]

This is the main content."""
    
    def test_compile_with_links(self, tmp_path):
        """Test compiling content with linked documents."""
        main_path = tmp_path / "Main.md"
        main_content = "Main document content."
        
        link1_path = tmp_path / "First.md"
        link2_path = tmp_path / "Second.md"
        
        linked_docs = [
            ("First", link1_path, "First document content."),
            ("Second", link2_path, "Second document content.")
        ]
        
        result = compile_content(main_path, main_content, linked_docs)
        
        expected = f"""# Main
[Source: {main_path}]

Main document content.

---

## Linked Documents (Depth 1)

### [[First]]
[Source: {link1_path}]

First document content.

### [[Second]]
[Source: {link2_path}]

Second document content."""
        
        assert result == expected