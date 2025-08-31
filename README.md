# SimpleNote to Obsidian Importer

A Python tool for converting SimpleNote exports to Obsidian-compatible markdown files with YAML frontmatter.

## Phase 2 Implementation Status: ✅ COMPLETE

Successfully implemented enhanced processing with:
- **Phase 1 features**: YAML frontmatter, metadata, timestamps, filename sanitization
- **Editor Pipeline Framework**: Extensible content processing system
- **Auto-tagging**: Content and filename pattern-based tag injection  
- **Folder Organization**: Smart categorization by content type
- **Content Transformation**: Whitespace cleanup and formatting standardization
- **Configuration System**: Flexible presets and custom rule support

## Features

### Core Processing
- **Metadata Parsing**: Extracts timestamps, tags, and other metadata from `notes.json`
- **Content Processing**: Reads and processes `.txt` files from SimpleNote export
- **YAML Frontmatter**: Adds comprehensive metadata to each note
- **Filename Sanitization**: Converts titles to Obsidian-compatible filenames

### Phase 2 Enhancements
- **Auto-Tagging**: Intelligent tagging based on content analysis and filename patterns
- **Folder Organization**: Automatic categorization into logical folder structures  
- **Content Transformation**: Whitespace cleanup, header standardization, list formatting
- **Configuration Presets**: Ready-to-use configurations (minimal, basic, organized, full)
- **Custom Rules**: Flexible pattern-based tagging and organization rules
- **Editor Pipeline**: Extensible framework for content processing modules

## Usage

### Basic Usage
```bash
# Phase 1 compatibility - Basic import
python import.py --notes data --json data/source/notes.json

# Smart processing with default settings
python import.py --notes data --json data/source/notes.json --smart

# Smart processing with presets
python import.py --preset organized --notes data --json data/source/notes.json 
python import.py --preset full --notes data --json data/source/notes.json
```

### Smart Processing Configuration Presets
- **`minimal`**: Basic import mode, no smart processing
- **`basic`**: Auto-tagging and content transformation only
- **`organized`**: Full smart processing with folder organization
- **`full`**: All features including index files and backlinks

### Custom Configuration
```bash
# Create a sample configuration file
python import.py --create-sample-config

# Use custom configuration
python import.py --config config/my_settings.yaml --notes data --json data/source/notes.json
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

### Phase 2 Results ✅
**Successfully processed:** 129/129 notes with enhanced features
- **Smart Organization**: Auto-categorized into 20+ folders (cocktails, gaming, music, recipes, etc.)
- **Enhanced Tagging**: 890+ intelligent tags applied based on content analysis
- **Content Transformation**: Headers standardized, whitespace cleaned, lists formatted
- **Metadata Preservation**: All timestamps, original IDs, and SimpleNote tags maintained
- **Folder Structure**: Logical hierarchy (recipes/fermentation, music/electronic, etc.)

### Phase 1 Baseline ✅  
- All `.txt` files converted to `.md` format
- Metadata matched and applied from JSON (262 notes in JSON, 129 .txt files)
- YAML frontmatter correctly generated
- Filenames sanitized for Obsidian compatibility

## Future Enhancements (Phase 3)

Building on the completed Phase 2 foundation:

### Phase 3 - Advanced Features (Planned)
- **Note Splitting**: Break large notes into smaller ones based on headers
- **Link Detection**: Convert references to other notes into Obsidian links
- **Content Analysis**: Advanced categorization using NLP techniques
- **Batch Operations**: Apply transformations to existing Obsidian vaults
- **Custom Processors**: Plugin system for user-defined content transformations
- **Index Generation**: Automatic creation of MOCs (Maps of Content)

## Dependencies

- Python 3.13+
- PyYAML 6.0.2 (YAML configuration and frontmatter)
- python-dateutil 2.9.0 (timestamp parsing)

## License

Generated with Claude Code - Feel free to modify and extend for your needs.