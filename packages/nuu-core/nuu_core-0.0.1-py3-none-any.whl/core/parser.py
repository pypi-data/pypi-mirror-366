"""Wiki link extraction utilities."""

import re
from typing import List


def extract_wiki_links(content: str) -> List[str]:
    """Extract wiki-style links from markdown content.
    
    Handles formats:
    - [[Simple Link]]
    - [[Link|Display Alias]]
    - [[Link#Section]]
    
    Args:
        content: Markdown content to parse
        
    Returns:
        List of link targets (without brackets or aliases)
    """
    # Regex pattern to match wiki links
    # Matches exactly two [[ followed by content and exactly two ]]
    # Uses negative lookahead/lookbehind to avoid matching more brackets
    pattern = r'(?<!\[)\[\[([^\[\]]+)\]\](?!\])'
    
    links: List[str] = []
    for match in re.finditer(pattern, content):
        link_content = match.group(1)
        
        # Handle alias format [[Link|Alias]] - extract just the link part
        if '|' in link_content:
            link_target = link_content.split('|')[0].strip()
        else:
            link_target = link_content.strip()
        
        # Handle section format [[Link#Section]] - keep the full link
        # The link target includes the section for now
        
        if link_target and link_target not in links:
            links.append(link_target)
    
    return links