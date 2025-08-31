# SimpleNote to Obsidian Import Plan

## Analysis Summary

After examining your SimpleNote export, here's what we're working with:

**Data Sources:**
- `.txt files` in root directory: Individual notes with clean markdown formatting
- `source/notes.json`: Contains metadata and full content with `\r\n` line endings

**Key Observations:**
1. The `.txt` files are already properly formatted with markdown
2. The JSON contains identical content but with Windows line endings (`\r\n`)
3. Notes have creation dates, modification dates, and some have markdown flags
4. File names in `.txt` format use clean titles (e.g., "# Rum Cocktails.txt")

## Recommendation: Use .txt Files

**Why .txt files over JSON:**
- Already have proper markdown formatting
- Clean filenames that work well in Obsidian
- No need to handle `\r\n` conversion
- Simpler processing pipeline

**Use JSON for:**
- Creation/modification timestamps
- Additional metadata if needed
- Mapping file names to IDs for cross-referencing

## Import Program Architecture

### Core Components

1. **Metadata Processor**
   - Parse `notes.json` to extract timestamps and metadata
   - Create filename-to-metadata mapping

2. **Content Processor** 
   - Read `.txt` files for content
   - Apply content transformations during import

3. **Editor Pipeline** (Extensible design for future enhancements)
   - Tag injection system
   - Note splitting logic
   - Content transformation rules

4. **Obsidian Formatter**
   - Add YAML frontmatter with metadata
   - Ensure proper markdown formatting
   - Handle special Obsidian features (links, tags)

### Program Flow

```
1. Parse notes.json → metadata mapping
2. Scan .txt files → content extraction  
3. For each note:
   a. Load content from .txt file
   b. Retrieve metadata from JSON mapping
   c. Apply editor pipeline transformations
   d. Format for Obsidian (add frontmatter)
   e. Write to output directory
```

### Editor Pipeline Design

The editor pipeline will be built with extensibility in mind:

```python
class EditorPipeline:
    def __init__(self):
        self.processors = []
    
    def add_processor(self, processor):
        # Add tag injection, note splitting, etc.
        pass
    
    def process(self, note_content, metadata):
        # Apply all processors in sequence
        pass
```

**Future Editor Capabilities:**
- **Auto-tagging**: Based on content analysis or filename patterns
- **Note splitting**: Break large notes into smaller ones based on headers
- **Link creation**: Convert references to other notes into Obsidian links
- **Content cleanup**: Remove/modify specific patterns
- **Category organization**: Sort into folders based on content type

### Output Structure

```
obsidian-vault/
├── cocktails/
│   ├── rum-cocktails.md
│   ├── gin-cocktails.md
│   └── whiskey-cocktails.md
├── gaming/
│   ├── elden-ring.md
│   └── hollow-knight.md
└── recipes/
    ├── fermentation/
    │   ├── kombucha.md
    │   └── kimchi.md
    └── hard-shell-tacos.md
```

### YAML Frontmatter Template

```yaml
---
title: "Original Note Title"
created: 2022-11-14T23:25:28.723Z
modified: 2025-07-20T00:36:25.092Z
source: "simplenote"
original_id: "8c1c6f2ee3fc4e78bceece8950e4a5a2"
tags: []
---
```

## Implementation Strategy

### Phase 1: Basic Import
- Simple 1:1 conversion of .txt files to .md files
- Add YAML frontmatter with timestamps
- Preserve original content structure

### Phase 2: Enhanced Processing  
- Implement editor pipeline framework
- Add basic auto-tagging based on filename patterns
- Create folder organization system

### Phase 3: Advanced Features
- Note splitting capabilities
- Link detection and creation
- Content-based categorization
- Custom transformation rules

## Technology Stack

**Language**: Python (for rich text processing libraries)

**Key Libraries**:
- `json` - Parse metadata
- `pathlib` - File system operations  
- `yaml` - Generate frontmatter
- `re` - Pattern matching for transformations
- `dateutil` - Date/time handling

## Next Steps

1. Create basic import script structure
2. Implement metadata parsing
3. Build content processing pipeline
4. Add editor framework for future extensibility
5. Test with a subset of notes
6. Iterate based on results

This approach provides a solid foundation while maintaining flexibility for the content editing and organization features you'll want to add later.