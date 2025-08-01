# NUU Core - Product Overview

## Executive Summary

NUU Core is a revolutionary CLI tool and knowledge management paradigm that transforms how humans and AI interact with information. Built on a "File-First, Markdown-Native Knowledge Substrate," it represents a fundamental shift from traditional database-centric systems to a future-proof, AI-compatible knowledge architecture where plain text files ARE the database, and file names ARE the schema.

## The Paradigm Shift

### Traditional Knowledge Management
- Databases/silos as source of truth
- Proprietary formats and vendor lock-in
- Opaque IDs and complex schemas
- AI bolted on as afterthought
- Platform-dependent backups

### NUU Core Philosophy
- **Markdown files = canonical records**
- **Human-readable titles = primary IDs**
- **Schema lives in naming conventions**
- **AI uses same grammar as humans**
- **Git-diffable, eternally portable**

> "Every idea is a plain-text file whose name itself encodes its coordinates in concept-space; all tooling is ephemeral."

## Core Innovation: Title-Dimension Architecture

### Syntactic Structure
```
Title        ::= Core concept (no parentheses/braces)
Subtitle     ::= '(' … ')' (optional, ordered)
Subsubtitle  ::= '{' … '}' (optional, nested)
FullTitle    ::= Title [Subtitle]* [Subsubtitle]*
```

### Examples
- `Surf` - Primary concept
- `Surf (MVP spec)` - Concept with context
- `Surf (API) {v0.1}` - Versioned specification

This creates a self-describing file system where:
- Earlier segments = permanence
- Later segments = ephemera
- Everything is human AND machine parseable

## Technical Architecture

### Core Components

1. **Index-on-Top Design**
   ```
   .core/index.json (volatile, rebuildable)
          ↑
   Git-tracked *.md files (source of truth)
          ↑
   Core CLI + LLM agents (same AST/grammar)
   ```

2. **Folder Structure**
   ```
   📁 /vault_root
   ├── 01 Vault/      # Long-lived semantic notes
   ├── 02 Journal/    # Daily notes (YYYY-MM-DD.md)
   ├── 03 Records/    # Raw data, transcripts
   ├── 04 Sources/    # External references
   └── .core.yml      # Configuration
   ```

3. **YAML Frontmatter**
   ```yaml
   ---
   title: "NUU Core Meeting"
   date: 2025-07-24
   type: meeting
   tags: [core, strategy]
   depth_default: 1
   ---
   ```

## CLI Capabilities

### Current Commands

#### `core fetch [file] [-d depth]`
- Retrieves file content plus linked documents
- Configurable traversal depth
- Outputs to clipboard or stdout
- Respects privacy tags and depth overrides

#### `core graph [concept] [--show N]`
- Visualizes knowledge connections
- ASCII or HTML output
- Quick navigation tool

### Planned Features
- `core new [type] [title]` - Scaffold from templates
- `core rename` - Safe renaming with backlink updates
- `core lint` - Find orphans, duplicates, conflicts
- `core export` - Generate various output formats
- `core patch` - AI-compatible edit operations

## Use Cases

### 1. AI-First Organization
Teams capture all knowledge in markdown, using the vault as a "second brain" that both humans and AI can query, understand, and augment.

### 2. Personal Knowledge Management
Individuals build a lifelong knowledge system that survives tool changes, syncs via Git, and grows organically.

### 3. Research & Academia
Scholars maintain citation graphs, evolving theories, and collaborative knowledge bases without proprietary lock-in.

### 4. Software Documentation
Projects maintain docs alongside code, with the same version control, review processes, and AI assistance.

## Why This Matters

### For Humans
- **No Learning Curve**: It's just files and folders
- **Tool Independence**: Works with any text editor
- **Version Control**: Full Git history of thoughts
- **Search-First**: Find by concept, not location

### For AI
- **Native Format**: Markdown AST is AI-friendly
- **Self-Describing**: Titles encode semantics
- **Consistent Grammar**: Same parsing rules everywhere
- **Context-Aware**: Links provide natural boundaries

### For the Future
- **Eternal Format**: Plain text outlasts all platforms
- **Composable**: Any tool can build on top
- **Distributed**: No central point of failure
- **Evolvable**: Schema changes without migration

## Technical Implementation

### Stack
- **Language**: Python 3.11+
- **CLI Framework**: Typer (built on Click)
- **Parser**: markdown-it-py
- **Dependencies**: Minimal (pyperclip, PyYAML)

### Design Principles
1. **Speed**: Instant file lookups via index
2. **Simplicity**: No databases, just files
3. **Compatibility**: Standard markdown everywhere
4. **Extensibility**: Plugin architecture planned

## Competitive Advantages

1. **Zero Vendor Lock-in**: It's just markdown files
2. **AI-Native**: Built for LLM consumption from day one
3. **Git-First**: Version control built into the paradigm
4. **Human-Readable**: No training needed
5. **Future-Proof**: Will outlast any company/platform

## Vision & Roadmap

### Phase 1: Foundation (Current)
- Core CLI tool with fetch/graph commands
- Basic vault conventions established
- Manual AI integration via clipboard

### Phase 2: Intelligence
- Automated indexing and embeddings
- Direct LLM integration
- Smart traversal algorithms

### Phase 3: Ecosystem
- Plugin system for extensions
- Multi-vault federation
- Real-time collaboration layers

### Phase 4: Paradigm Shift
- Industry adoption of file-first philosophy
- Standard protocols for knowledge interchange
- New academic discipline around "Cognitive Engineering"

## Business Model

### Open Core Approach
- **Core CLI**: Open source (MIT license)
- **Pro Features**: Enhanced AI integration, team sync
- **Enterprise**: Private vault hosting, compliance tools
- **Consulting**: Vault architecture, migration services

## Call to Action

NUU Core isn't just a tool—it's a movement toward sustainable, human-centric knowledge management. By putting files first and making everything else ephemeral, we're building a foundation that will outlast today's platforms and tomorrow's AI models.

Join us in creating an operating system for human knowledge that's as simple as files in folders, yet powerful enough to augment human cognition at scale.

---

*"The best knowledge system is the one that's still readable in 100 years. With NUU Core, that's not a hope—it's a guarantee."*