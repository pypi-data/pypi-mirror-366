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

## User Stories

### Story 1.1: Repository Setup and Project Structure
**Priority**: High  
**Estimate**: 2 hours  

**Story Statement**:  
As a developer, I want a properly structured Python project with minimal dependencies so that I can build and distribute the NUU Core CLI tool.

**Acceptance Criteria**:
1. Python project structure follows modern best practices (pyproject.toml based)
2. Minimal dependencies installed (typer, pyperclip, pyyaml)
3. Basic CLI entry point that prints version
4. README with installation instructions
5. .gitignore for Python projects
6. MIT License file

### Story 1.2: Implement Basic Fetch with Wiki Links (Depth 1)
**Priority**: High  
**Estimate**: 4 hours  

**Story Statement**:  
As a user, I want to fetch a markdown file and its wiki-linked documents at depth 1 so that I can copy the compiled content to my clipboard for AI consumption.

**Acceptance Criteria**:
1. CLI accepts file identifier as argument
2. Finds markdown file by title (case-insensitive exact match)
3. Extracts all [[wiki links]] from the content
4. Fetches each linked file (depth 1 only)
5. Compiles content in specified format with source paths
6. Copies final output to system clipboard
7. Shows success message with word count
8. Handles missing files gracefully with warnings

## Technical Constraints
- Python 3.11+ only
- Use typer for CLI framework
- Use pyperclip for clipboard operations
- No caching or indexing
- Wiki links only in MVP

## Out of Scope
- Configuration files
- Multiple link formats (markdown links, etc)
- Variable depth beyond 1
- File watching
- Advanced search or partial matching