# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a SimpleNote to Obsidian importer - a Python tool for converting SimpleNote exports to Obsidian-compatible markdown files with YAML frontmatter. Currently at Phase 1 implementation (basic 1:1 conversion complete), with architecture designed for future phases including advanced content processing and organization.

## Development Commands

### Environment Setup
```bash
# Use pre-configured virtual environment
obsidian-porter/Scripts/python <command>

# Or activate environment (Windows)
obsidian-porter\Scripts\activate
```

### Running the Importer
```bash
# Basic import from current directory
python import.py

# Import with all options
python import.py --notes path/to/notes --json path/to/source/notes.json --output output/vault

# Help and options
python import.py --help

# Direct execution via venv
obsidian-porter/Scripts/python import.py --notes simpleNotes-notes --json simpleNotes-notes/source/notes.json --output output/test
```

### Dependencies
```bash
# Install requirements (already done in venv)
pip install -r requirements.txt

# Key dependencies: PyYAML==6.0.2, python-dateutil==2.9.0.post0
```

## Architecture Overview

### Core Processing Pipeline
The importer follows a 3-step pipeline orchestrated by `SimpleNoteImporter`:

1. **Metadata Parsing** (`MetadataParser`) - Extracts timestamps, tags, and metadata from `notes.json`
2. **Content Processing** (`ContentProcessor`) - Reads and processes `.txt` files from SimpleNote export  
3. **Obsidian Formatting** (`ObsidianFormatter`) - Generates markdown with YAML frontmatter

### Component Interactions
- `SimpleNoteImporter` orchestrates the entire process and handles CLI interface
- `MetadataParser` creates filename-to-metadata mapping from JSON export
- `ContentProcessor` handles file discovery and content extraction from .txt files
- `ObsidianFormatter` combines content with metadata to create Obsidian-compatible files

### Data Flow Architecture
```
SimpleNote Export (.txt files + source/notes.json)
    ↓
MetadataParser → filename-to-metadata mapping
    ↓
ContentProcessor → note content + basic info
    ↓  
ObsidianFormatter → .md files with YAML frontmatter
    ↓
Output directory (Obsidian vault)
```

### Extensibility Design
The architecture is built for future enhancement phases:
- **Editor Pipeline Framework** (planned Phase 2) - Pluggable content transformations
- **Auto-tagging and Organization** (planned Phase 2) - Content-based categorization
- **Advanced Features** (planned Phase 3) - Note splitting, link creation, custom rules

### Entry Points
- `import.py` - Main CLI entry point that adds `src/` to Python path
- `src/simplenote_importer.py` - Contains main application logic and argument parsing
- `src/__init__.py` - Package exports for programmatic usage

### File Structure Expectations
The importer expects SimpleNote export format:
- `.txt` files in root directory (actual note content)
- `source/notes.json` (metadata with timestamps, tags, IDs)
- Output goes to specified directory or `{notes_dir}/obsidian_vault`

### YAML Frontmatter Schema
Generated notes include standardized frontmatter:
- `title` - Note title (from first line)
- `created`/`modified` - ISO timestamps from JSON metadata  
- `source` - Always "simplenote"
- `original_id` - SimpleNote ID for reference
- `tags` - Array of tags from SimpleNote
- `markdown`/`pinned` - Boolean flags from SimpleNote

## Key Implementation Details

### Filename Sanitization
The `ObsidianFormatter._sanitize_filename()` method handles conversion of SimpleNote titles to Obsidian-compatible filenames, replacing invalid characters and handling conflicts with numeric suffixes.

### Metadata Matching Strategy  
The `MetadataParser._generate_filename()` method creates the same filename pattern as SimpleNote's .txt export, enabling reliable metadata matching between JSON and .txt files.

### Error Handling
The main importer provides comprehensive error handling with detailed progress reporting and summary statistics, including warnings for partial failures.

### Phase 1 Status
Phase 1 implementation is complete and tested with 129/129 notes successfully processed. The codebase is ready for Phase 2 enhancements following the planned architecture in `.agents/plans/simplenote-to-obsidian-import-plan.md`.