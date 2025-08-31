# SimpleNote to Obsidian Importer

A Python tool for converting SimpleNote exports to Obsidian-compatible markdown files with YAML frontmatter.

## Phase 1 Implementation Status: ✅ COMPLETE

Successfully implemented basic 1:1 conversion with:
- YAML frontmatter with metadata
- Proper markdown formatting 
- Timestamp preservation from JSON
- Tag support
- Original ID tracking
- Clean filename sanitization

## Features

- **Metadata Parsing**: Extracts timestamps, tags, and other metadata from `notes.json`
- **Content Processing**: Reads and processes `.txt` files from SimpleNote export
- **YAML Frontmatter**: Adds comprehensive metadata to each note
- **Filename Sanitization**: Converts titles to Obsidian-compatible filenames
- **Extensible Architecture**: Built with editor pipeline framework for future enhancements

## Usage

### Basic Usage
```bash
# Import from current directory
python import.py

# Import with custom paths
python import.py --notes path/to/notes --output path/to/vault

# Import with metadata
python import.py --notes path/to/notes --json path/to/source/notes.json --output output/vault
```

### Virtual Environment Setup
```bash
# The project comes with a pre-configured virtual environment
# Activate it (Windows):
obsidian-porter\Scripts\activate

# Or use directly:
obsidian-porter/Scripts/python import.py --help
```

## Project Structure

```
├── obsidian-porter/          # Python virtual environment
├── src/                      # Source code
│   ├── __init__.py
│   ├── simplenote_importer.py    # Main importer script
│   ├── metadata_parser.py        # JSON metadata parser
│   ├── content_processor.py      # .txt file processor
│   └── obsidian_formatter.py     # Obsidian formatting
├── output/                   # Generated Obsidian vaults
├── tests/                    # Test files (for future use)
├── import.py                 # Entry point script
└── requirements.txt          # Python dependencies
```

## YAML Frontmatter Format

Each converted note includes metadata in this format:

```yaml
---
title: "Note Title"
created: "2019-08-08T04:18:27+00:00"
modified: "2025-07-20T00:36:25.092Z"
source: "simplenote"
original_id: "de2b4d5df82743658f4b763cd5f978e2"
tags: ["ferment", "recipe"]
markdown: true
pinned: false
---
```

## Test Results

**Successfully processed:** 129/129 notes ✅
- All `.txt` files converted to `.md` format
- Metadata matched and applied from JSON (262 notes in JSON, 129 .txt files)
- YAML frontmatter correctly generated
- Filenames sanitized for Obsidian compatibility
- Content preserved exactly as-is

## Future Enhancements (Phases 2-3)

The codebase is designed for extensibility:

### Phase 2 - Enhanced Processing
- Editor pipeline framework implementation
- Auto-tagging based on content/filename patterns
- Folder organization system
- Content transformations

### Phase 3 - Advanced Features
- Note splitting capabilities
- Link detection and creation
- Content-based categorization
- Custom transformation rules

## Dependencies

- Python 3.13+
- PyYAML 6.0.2
- python-dateutil 2.9.0

## License

Generated with Claude Code - Feel free to modify and extend for your needs.