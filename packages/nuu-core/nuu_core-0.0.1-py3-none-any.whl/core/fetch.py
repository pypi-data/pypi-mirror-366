"""Document fetching and file resolution utilities."""

import re
from pathlib import Path
from typing import List, Tuple


class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found."""
    pass


def find_markdown_file(identifier: str, vault_path: Path = Path(".")) -> Path:
    """Find a markdown file by title (case-insensitive).
    
    Args:
        identifier: File title to search for
        vault_path: Root directory to search in
        
    Returns:
        Path to the found markdown file
        
    Raises:
        DocumentNotFoundError: If no matching file is found
    """
    identifier_lower = identifier.lower()
    
    # Search for .md files in vault_path and subdirectories
    for md_file in vault_path.rglob("*.md"):
        # Get the filename without extension
        file_title = md_file.stem
        
        # Case-insensitive exact match
        if file_title.lower() == identifier_lower:
            return md_file
    
    # If no file found, raise error
    raise DocumentNotFoundError(f"Document '{identifier}' not found in vault")


def fetch_document(file_identifier: str, depth: int = 1, vault_path: Path = Path("."), tag: str | None = None) -> Tuple[str, List[str]]:
    """Fetch a document and its linked content.
    
    Args:
        file_identifier: Title or path of the document
        depth: Link traversal depth (only 1 supported in MVP)
        vault_path: Root directory to search in
        tag: Optional tag suffix to append to linked documents
        
    Returns:
        Tuple of (compiled markdown content, list of warnings)
    """
    if depth != 1:
        raise ValueError("Only depth=1 is supported in MVP")
    
    warnings: List[str] = []
    
    # Find the main document
    try:
        main_doc_path = find_markdown_file(file_identifier, vault_path)
    except DocumentNotFoundError:
        raise
    
    # Read main document content
    main_content = main_doc_path.read_text(encoding='utf-8')
    
    # Extract wiki links with original formatting
    wiki_link_pattern = r'(?<!\[)\[\[([^\[\]]+)\]\](?!\])'
    wiki_links_raw: List[str] = []
    wiki_links_targets: List[str] = []
    
    for match in re.finditer(wiki_link_pattern, main_content):
        full_link = match.group(1)
        wiki_links_raw.append(full_link)
        
        # Extract target for file lookup
        if '|' in full_link:
            target = full_link.split('|')[0].strip()
        else:
            target = full_link.strip()
        wiki_links_targets.append(target)
    
    # Track visited files to avoid duplicates
    visited = {main_doc_path}
    seen_links: set[str] = set()  # Track which raw links we've already processed
    
    # Fetch linked documents
    linked_docs: List[Tuple[str, Path, str]] = []
    for raw_link, target_link in zip(wiki_links_raw, wiki_links_targets):
        # Skip if we've seen this exact link before
        if raw_link in seen_links:
            continue
        seen_links.add(raw_link)
        
        # Remove section references for file lookup
        file_identifier = target_link.split('#')[0] if '#' in target_link else target_link
        
        # Apply tag suffix if provided
        if tag:
            file_identifier = f"{file_identifier} {{{tag}}}"
        
        try:
            linked_path = find_markdown_file(file_identifier, vault_path)
            if linked_path not in visited:
                visited.add(linked_path)
                linked_content = linked_path.read_text(encoding='utf-8')
                linked_docs.append((raw_link, linked_path, linked_content))
        except DocumentNotFoundError:
            warnings.append(f"Could not find linked document '{file_identifier}'")
        except Exception as e:
            warnings.append(f"Error reading linked document '{file_identifier}': {str(e)}")
    
    # Compile the content
    compiled = compile_content(main_doc_path, main_content, linked_docs, tag)
    
    return compiled, warnings


def compile_content(main_path: Path, main_content: str, linked_docs: List[Tuple[str, Path, str]], tag: str | None = None) -> str:
    """Compile the main document and linked documents into final output.
    
    Args:
        main_path: Path to the main document
        main_content: Content of the main document
        linked_docs: List of (link_text, path, content) tuples for linked documents
        tag: Optional tag suffix to append to linked document titles
        
    Returns:
        Compiled markdown content
    """
    # Extract title from main document
    main_title = main_path.stem
    
    # Build output
    output_parts: List[str] = []
    
    # Main document
    output_parts.append(f"# {main_title}")
    output_parts.append(f"[Source: {main_path}]")
    output_parts.append("")
    output_parts.append(main_content.strip())
    
    # Add linked documents if any
    if linked_docs:
        output_parts.append("")
        output_parts.append("---")
        output_parts.append("")
        output_parts.append("## Linked Documents (Depth 1)")
        
        for link_text, link_path, link_content in linked_docs:
            output_parts.append("")
            # Apply tag to the link display if provided
            if tag:
                # Check if link already has a display name
                if '|' in link_text:
                    target, display = link_text.split('|', 1)
                    display_text = f"{target} {{{tag}}}|{display}"
                else:
                    display_text = f"{link_text} {{{tag}}}"
            else:
                display_text = link_text
            output_parts.append(f"### [[{display_text}]]")
            output_parts.append(f"[Source: {link_path}]")
            output_parts.append("")
            output_parts.append(link_content.strip())
    
    return "\n".join(output_parts)