# Product Requirements Document: NUU Core MVP
## Core Fetch Command

### Document Information
- **Version**: 1.0
- **Date**: 2025-01-30
- **Author**: Product Team
- **Status**: Draft

### Executive Summary

This PRD defines the Minimum Viable Product (MVP) for NUU Core - a CLI tool that fetches markdown content and its linked documents, then copies the compiled result to the clipboard. This MVP demonstrates the core value proposition: making knowledge in markdown vaults easily accessible for AI consumption.

### Problem Statement

Users maintaining markdown-based knowledge vaults (Obsidian, plain markdown folders) need to quickly gather context from interconnected documents for:
- Pasting into AI chat interfaces (ChatGPT, Claude)
- Sharing comprehensive context with team members
- Creating self-contained document exports

Current solutions require manual copy-pasting of multiple files, losing link relationships and context.

### Solution Overview

A command-line tool that:
1. Accepts a file identifier (title or path)
2. Fetches the file content
3. Recursively fetches linked documents (configurable depth)
4. Compiles everything into a single, organized output
5. Copies to system clipboard

### User Personas

1. **AI Power User**
   - Uses ChatGPT/Claude daily
   - Maintains personal knowledge vault
   - Needs quick context loading

2. **Technical Knowledge Worker**
   - Documents projects in markdown
   - Collaborates via shared contexts
   - Values speed and simplicity

### Success Metrics

- **Adoption**: 100+ users within first month
- **Performance**: <1 second for typical fetch operations
- **Reliability**: 99% success rate for clipboard operations
- **Simplicity**: <5 minute setup time

### Functional Requirements

#### Core Command: `nuu fetch`

**Basic Usage**
```bash
nuu fetch "Meeting Notes"
nuu fetch meeting-notes.md
nuu fetch "Project Plan" -d 2
```

**Parameters**
- `file`: File identifier (title match or path)
- `-d, --depth`: Link traversal depth (default: 1, max: 3)
- `--no-copy`: Output to stdout instead of clipboard
- `-v, --verbose`: Show progress information

**File Resolution**
1. Exact title match (case-insensitive)
2. Partial title match
3. Filename match
4. Path match
5. If multiple matches: show numbered list for selection

**Link Detection**
- Wiki-style: `[[File Name]]`
- Wiki with anchor: `[[File Name#Section]]`
- Wiki with alias: `[[File Name|Display Text]]`
- Markdown links: `[text](./path/to/file.md)`

**Output Format**
```markdown
# Main Document Title
[Source: /path/to/file.md]

[Main document content...]

---

## Linked Documents (Depth 1)

### [[Linked Doc 1]]
[Source: /path/to/linked1.md]

[Linked document content...]

### [[Linked Doc 2]]
[Source: /path/to/linked2.md]

[Linked document content...]
```

**Traversal Rules**
1. Avoid circular references (track visited files)
2. Respect depth limit strictly
3. Skip missing/broken links with warning
4. Ignore external URLs
5. Skip binary files (images, PDFs)

#### Configuration

**File**: `.nuu/config.yml` or `~/.config/nuu/config.yml`

```yaml
# Default configuration
vault_path: "."  # Current directory
default_depth: 1
max_depth: 3
ignore_patterns:
  - "*.tmp"
  - ".git/**"
  - "node_modules/**"
ignore_tags:
  - "private"
  - "draft"
clipboard_timeout: 5  # seconds
```

### Non-Functional Requirements

#### Performance
- Fetch 10 documents in <1 second
- Handle vaults with 10,000+ files
- Clipboard operations <100ms

#### Reliability
- Graceful handling of missing files
- Clear error messages
- No data loss or corruption
- Cross-platform clipboard support

#### Usability
- Single binary distribution
- No runtime dependencies
- Clear --help documentation
- Intuitive error messages

### Technical Constraints

1. **Language**: Python 3.11+
2. **Dependencies**: Minimal
   - `click` or `typer` for CLI
   - `pyperclip` for clipboard
   - `pyyaml` for config
   - `pathlib` for file operations
3. **Platform Support**: macOS, Linux, Windows
4. **Distribution**: Single executable via PyInstaller

### Out of Scope (MVP)

1. GUI or web interface
2. Vault indexing/caching
3. Edit operations
4. Git integration
5. Plugin system
6. Advanced search
7. Export formats (PDF, HTML)
8. Multi-vault support
9. Real-time sync
10. Collaborative features

### Development Phases

#### Phase 1: Core Functionality (Week 1)
- [ ] Project setup and structure
- [ ] Basic file reading
- [ ] Link detection regex
- [ ] Depth-first traversal
- [ ] Output formatting

#### Phase 2: Clipboard & Config (Week 2)
- [ ] Cross-platform clipboard
- [ ] Configuration file parsing
- [ ] Ignore patterns
- [ ] Error handling

#### Phase 3: Polish & Release (Week 3)
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Installation guide
- [ ] Binary packaging

### Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Clipboard library compatibility | High | Test on all platforms early |
| Large vault performance | Medium | Implement streaming reads |
| Complex link formats | Low | Start with basic formats |
| Circular reference loops | Medium | Visited set tracking |

### Testing Strategy

1. **Unit Tests**
   - Link detection patterns
   - File resolution logic
   - Traversal algorithm

2. **Integration Tests**
   - Real vault structures
   - Various link formats
   - Edge cases (missing files, cycles)

3. **User Acceptance**
   - 5 beta users
   - Real-world vaults
   - Feedback iteration

### Launch Plan

1. **Soft Launch**
   - Personal network (10 users)
   - GitHub release
   - Basic documentation

2. **Feedback Integration**
   - Daily standup reviews
   - Quick iteration cycles
   - Version 1.1 planning

3. **Public Announcement**
   - Blog post
   - Product Hunt (optional)
   - Obsidian forum post

### Success Criteria

The MVP is successful if:
1. Users can fetch any document with links in <5 commands
2. Output is correctly formatted for AI consumption
3. No critical bugs in first week
4. 80% of beta users want to keep using it
5. Clear path to next features identified

### Future Considerations

Based on MVP feedback, consider:
- Caching/indexing for speed
- More output formats
- Integration with AI APIs
- Vault statistics/insights
- Collaborative features

---

### Appendix A: Example Usage Scenarios

**Scenario 1: Meeting Context**
```bash
$ nuu fetch "Team Standup 2025-01-30"
✓ Found: Team Standup 2025-01-30.md
✓ Fetching 3 linked documents...
✓ Copied to clipboard (2,847 words)
```

**Scenario 2: Project Documentation**
```bash
$ nuu fetch "API Design" -d 2
✓ Found: API Design.md
✓ Fetching links (depth 1): 5 documents
✓ Fetching links (depth 2): 12 documents  
✓ Copied to clipboard (8,392 words)
```

**Scenario 3: Multiple Matches**
```bash
$ nuu fetch "meeting"
Multiple matches found:
1. Team Meeting 2025-01-28.md
2. Client Meeting Notes.md
3. Meeting Templates/Weekly.md
Select file (1-3): 2
✓ Fetching: Client Meeting Notes.md
✓ Copied to clipboard (1,203 words)
```