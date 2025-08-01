# Epic 001: NUU Core MVP - Basic Fetch Command

## Epic Overview
**Epic ID**: EPIC-001  
**Title**: NUU Core MVP - Basic Fetch Command  
**Goal**: Deliver a minimal CLI tool that can fetch markdown documents with their linked references and copy to clipboard  
**Priority**: High  
**Target Completion**: 1 week  

## Business Value
Enable users to quickly gather markdown content and linked documents for AI consumption, demonstrating the core value proposition of the file-first knowledge paradigm.

## Success Criteria
1. Users can fetch any markdown file by title
2. Tool follows [[wiki links]] to depth 1
3. Output is copied to clipboard
4. Clear installation and usage instructions
5. Works on macOS/Linux (Windows stretch goal)

## Stories
1. **STORY-001**: Repository Setup and Project Structure
2. **STORY-002**: Implement Basic Fetch with Wiki Links (Depth 1)

## Constraints
- Python 3.11+ only
- Minimal dependencies
- No caching/indexing in MVP
- Wiki links only (no markdown links)
- Fixed depth of 1

## Out of Scope
- Configuration files
- Multiple link formats
- Variable depth
- File watching
- Advanced search