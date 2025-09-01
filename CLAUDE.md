# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a SimpleNote to Obsidian importer - a Python tool for converting SimpleNote exports to Obsidian-compatible markdown files with YAML frontmatter. Currently at Phase 2 implementation (enhanced processing complete) with auto-tagging, folder organization, and content transformation features. Architecture designed for Phase 3 advanced features.

## Development Commands

### Git Workflow
```bash
# Before starting work on any task, create a new branch
git checkout -b feature/task-description
git checkout -b fix/issue-description
git checkout -b enhancement/feature-name

# Examples:
git checkout -b feature/phase3-note-splitting
git checkout -b fix/metadata-parsing-bug
git checkout -b enhancement/advanced-tagging
```

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

# Smart processing with organized preset
obsidian-porter/Scripts/python import.py --preset organized --notes data --json data/source/notes.json --output output/organized

# Smart processing with custom config
obsidian-porter/Scripts/python import.py --config config/my_settings.yaml --notes data --json data/source/notes.json

# Smart processing with default settings
obsidian-porter/Scripts/python import.py --smart --notes data --json data/source/notes.json

# Create sample configuration
obsidian-porter/Scripts/python import.py --create-sample-config
```

### Dependencies
```bash
# Install requirements (already done in venv)
pip install -r requirements.txt

# Key dependencies: PyYAML==6.0.2, python-dateutil==2.9.0.post0
```

### Testing
```bash
# Run all tests
obsidian-porter/Scripts/python -m pytest

# Run tests with coverage
obsidian-porter/Scripts/python -m pytest --cov=src --cov-report=html

# Run specific test categories
obsidian-porter/Scripts/python -m pytest tests/unit/
obsidian-porter/Scripts/python -m pytest tests/integration/

# Run tests in verbose mode
obsidian-porter/Scripts/python -m pytest -v

# Run tests and stop on first failure
obsidian-porter/Scripts/python -m pytest -x
```

#### Testing Guidelines
- **Always write tests** for new features and bug fixes
- **Update tests** when refactoring existing code
- **Use dependency injection** when creating classes to make them easier to test:
  - Accept file system interfaces instead of direct file operations
  - Pass configuration objects as parameters rather than loading internally
  - Inject external dependencies (parsers, formatters, etc.) through constructor
  - Return structured data that can be verified independently
- **Create unit tests** for individual components and methods
- **Create integration tests** for complete workflows and user scenarios
- **Use synthetic test data** - never commit real user notes or sensitive data
- **Aim for >90% test coverage** on core business logic
- **Keep tests fast and deterministic** - no external dependencies or random data

## Architecture Overview

### Core Processing Pipeline
The importer follows a 4-step pipeline orchestrated by `SimpleNoteImporter`:

1. **Metadata Parsing** (`MetadataParser`) - Extracts timestamps, tags, and metadata from `notes.json`
2. **Content Processing** (`ContentProcessor`) - Reads and processes `.txt` files from SimpleNote export
3. **Editor Pipeline** (`EditorPipeline`) - Phase 2: Auto-tagging, folder organization, content transformation
4. **Obsidian Formatting** (`ObsidianFormatter`) - Generates markdown with YAML frontmatter and folder structure

### Component Interactions
- `SimpleNoteImporter` orchestrates the entire process and handles CLI interface + configuration
- `MetadataParser` creates filename-to-metadata mapping from JSON export
- `ContentProcessor` handles file discovery and content extraction from .txt files
- `EditorPipeline` applies configurable content transformations (Phase 2)
  - `TagInjector` - Pattern-based auto-tagging
  - `FolderOrganizer` - Content-based folder assignment
  - `ContentTransformer` - Whitespace and formatting cleanup
- `ObsidianFormatter` combines content with metadata and creates organized folder structure
- `ImportConfig` + `ConfigManager` - Configuration system with presets and validation

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

### Phase 2 Status
Phase 2 implementation is complete and tested with 129/129 notes successfully processed. Features include:
- **Auto-tagging**: 890+ intelligent tags applied based on content patterns
- **Folder Organization**: Notes automatically categorized into 20+ logical folders
- **Content Transformation**: Standardized headers, cleaned whitespace, formatted lists
- **Configuration System**: 4 presets (minimal, basic, organized, full) plus custom config support
- **Backward Compatibility**: Phase 1 mode available via `minimal` preset

The codebase is ready for Phase 3 enhancements (note splitting, link detection, advanced NLP features).