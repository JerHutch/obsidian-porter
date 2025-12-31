# SimpleNote to Obsidian Importer (C# Edition)

A modern .NET 9 tool for converting SimpleNote exports to Obsidian-compatible markdown files with YAML frontmatter. This is a complete C# reimplementation of the Python version, featuring the same functionality with improved performance and modern C# patterns.

## Features

### Core Processing
- **Metadata Parsing**: Extracts timestamps, tags, and other metadata from `notes.json`
- **Content Processing**: Reads and processes `.txt` files from SimpleNote export
- **YAML Frontmatter**: Adds comprehensive metadata to each note
- **Filename Sanitization**: Converts titles to Obsidian-compatible filenames

### Smart Processing (Editor Pipeline)
- **Auto-Tagging**: Intelligent tagging based on content analysis and filename patterns
- **Folder Organization**: Automatic categorization into logical folder structures
- **Content Transformation**: Whitespace cleanup, header standardization, list formatting
- **Configuration System**: Flexible YAML-based configuration

## Requirements

- [.NET 9 SDK](https://dotnet.microsoft.com/download/dotnet/9.0)

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd obsidian-porter
```

2. Build the project:
```bash
cd src
dotnet build
```

### Basic Usage

```bash
# Basic import (minimal processing)
dotnet run --project ObsidianPorter.Cli -- --notes data --json data/source/notes.json

# Smart processing (auto-tagging, folder organization, content transformation)
dotnet run --project ObsidianPorter.Cli -- --notes data --json data/source/notes.json --smart

# Custom output directory
dotnet run --project ObsidianPorter.Cli -- --notes data --json data/source/notes.json --output my-vault

# Using a configuration file
dotnet run --project ObsidianPorter.Cli -- --config config/my-config.yaml --notes data --json data/source/notes.json
```

### Command-Line Options

```
Options:
  -n, --notes <notes>    Path to the directory containing SimpleNote .txt files [default: data]
  -j, --json <json>      Path to the notes.json metadata file [default: data/source/notes.json]
  -o, --output <output>  Path to the output directory for Obsidian vault [default: output/obsidian_vault]
  -c, --config <config>  Path to configuration YAML file (optional)
  --smart                Enable smart processing (auto-tagging, folder organization, content transformation)
  --version              Show version information
  -?, -h, --help         Show help and usage information
```

## Configuration

### Smart Processing

Smart processing enables the editor pipeline with automatic content enhancements:

```bash
# Enable with --smart flag
dotnet run --project ObsidianPorter.Cli -- --smart --notes data --json data/source/notes.json
```

Smart processing includes:
- **Auto-Tagging**: Adds tags based on content patterns (e.g., "cocktails", "recipes", "lists")
- **Folder Organization**: Organizes notes into folders based on tags/categories
- **Content Transformation**: Cleans whitespace, standardizes headers, fixes list formatting

### Custom Configuration

Create a YAML configuration file for advanced customization:

```yaml
# config/my-config.yaml
EnableEditorPipeline: true
EnableAutoTagging: true
EnableFolderOrganization: true
EnableContentTransformation: true

# Content transformation options
CleanWhitespace: true
StandardizeHeaders: true
FixListFormatting: true

# Folder organization
CustomFolderRules:
  gaming: "games"
  music: "audio/music"

# Custom tagging rules
CustomTagRules:
  "cocktail|drink|recipe": ["cocktails", "beverages"]
  "code|programming": ["development"]

PropagateCategoryTag: true
```

Use the configuration file:

```bash
dotnet run --project ObsidianPorter.Cli -- --config config/my-config.yaml --notes data --json data/source/notes.json
```

## Testing

The project includes comprehensive test coverage with 49+ tests:

```bash
# Run all tests
cd src
dotnet test

# Run tests with coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific test categories
dotnet test --filter "FullyQualifiedName~Unit"
dotnet test --filter "FullyQualifiedName~Integration"

# Run tests in verbose mode
dotnet test -v normal
```

### Test Coverage

- **Unit Tests**: Individual component testing (Parsers, Formatters, Processors, Configuration)
- **Integration Tests**: Full pipeline testing with various configurations
- **49+ Tests**: Comprehensive coverage of core business logic

## Project Structure

```
src/
├── ObsidianPorter.sln                    # Solution file
├── ObsidianPorter.Core/                  # Core business logic library
│   ├── Interfaces/
│   │   ├── IFileSystemService.cs         # File system abstraction
│   │   └── IContentProcessor.cs          # Pipeline processor interface
│   ├── Models/
│   │   ├── NoteMetadata.cs              # Note metadata record
│   │   ├── ProcessedNote.cs             # Processed note record
│   │   ├── ImportConfig.cs              # Configuration model
│   │   └── ImportResult.cs              # Import result record
│   ├── Services/
│   │   ├── MetadataParser.cs            # JSON metadata parser
│   │   ├── ContentProcessor.cs          # .txt file processor
│   │   ├── EditorPipeline.cs           # Pipeline orchestrator
│   │   ├── ObsidianFormatter.cs        # YAML frontmatter generator
│   │   ├── SimpleNoteImporter.cs       # Main import orchestrator
│   │   ├── ConfigManager.cs            # Configuration management
│   │   └── FileSystemService.cs        # File system implementation
│   └── Pipelines/
│       ├── BaseContentProcessor.cs      # Base processor class
│       ├── TagInjector.cs              # Auto-tagging processor
│       ├── ContentTransformer.cs       # Content cleanup processor
│       └── FolderOrganizer.cs          # Folder assignment processor
├── ObsidianPorter.Cli/                  # Command-line application
│   └── Program.cs                       # CLI entry point
└── ObsidianPorter.Tests/                # Test project
    ├── Unit/                            # Unit tests
    ├── Integration/                     # Integration tests
    └── Fixtures/                        # Test data and helpers
```

## Architecture

The importer follows a 4-step pipeline architecture:

1. **Metadata Parsing** (`MetadataParser`) - Extracts metadata from `notes.json`
2. **Content Processing** (`ContentProcessor`) - Reads `.txt` files
3. **Editor Pipeline** (`EditorPipeline`) - Applies transformations (optional)
   - Tag Injector
   - Content Transformer
   - Folder Organizer
4. **Obsidian Formatting** (`ObsidianFormatter`) - Generates markdown with YAML frontmatter

### Modern C# Features

- **Primary Constructors**: Simplified dependency injection
- **Record Types**: Immutable data models
- **File-Scoped Namespaces**: Reduced indentation
- **Collection Expressions**: Modern syntax (e.g., `[]` for empty arrays)
- **Nullable Reference Types**: Improved null safety
- **Pattern Matching**: Enhanced type checking
- **Source Generators**: Regex source generators for performance

## YAML Frontmatter Format

Each converted note includes metadata in this format:

```yaml
---
title: "Note Title"
created: "2024-01-01T12:00:00+00:00"
modified: "2024-01-02T14:30:00+00:00"
source: "simplenote"
original_id: "abc123def456"
tags:
  - tag1
  - tag2
markdown: true
pinned: false
category: "recipes"
---

Note content goes here...
```

## Performance

The C# implementation offers significant performance improvements over the Python version:

- **Faster Startup**: Native compilation, no interpreter overhead
- **Better Memory Usage**: Efficient memory management with modern .NET runtime
- **Concurrent Processing**: Built-in support for parallel operations (future enhancement)
- **Optimized Regex**: Source-generated regex patterns

## Migration from Python Version

The C# version maintains 100% compatibility with the Python version's output format. You can use either version interchangeably.

### Key Differences

- **Configuration**: YAML configuration format is identical
- **CLI Arguments**: Same arguments with additional options
- **Output**: Identical YAML frontmatter and markdown output
- **Performance**: C# version is significantly faster for large datasets

### Migrating Configuration

Python configuration files work as-is with the C# version:

```bash
# Python version
python import.py --config config/my-settings.yaml --notes data --json data/source/notes.json

# C# version (same config file)
dotnet run --project ObsidianPorter.Cli -- --config config/my-settings.yaml --notes data --json data/source/notes.json
```

## Development

### Building from Source

```bash
# Clone repository
git clone <repository-url>
cd obsidian-porter/src

# Restore dependencies
dotnet restore

# Build
dotnet build

# Run tests
dotnet test

# Build release version
dotnet build -c Release
```

### Adding Custom Processors

Implement the `IContentProcessor` interface:

```csharp
public class MyCustomProcessor : BaseContentProcessor
{
    public override string Name => "my_processor";

    public override (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context)
    {
        // Your processing logic here
        return (modifiedContent, updatedMetadata);
    }
}
```

## Legacy Python Implementation

The original Python implementation is preserved in the `python-version/` directory for reference. Both versions produce identical output and share the same configuration format.

## License

Generated with Claude Code - Feel free to modify and extend for your needs.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`dotnet test`)
- Code follows existing patterns
- New features include tests
- Documentation is updated

## Troubleshooting

### Common Issues

**Issue**: `dotnet: command not found`
- **Solution**: Install .NET 9 SDK from https://dotnet.microsoft.com/download

**Issue**: Tests fail with file access errors
- **Solution**: Ensure you have write permissions in the test directory

**Issue**: Configuration file not found
- **Solution**: Check the path is correct and the file exists

### Getting Help

- Check the [Python version documentation](python-version/README.md) for conceptual information
- Review test files for usage examples
- Open an issue on GitHub

## Changelog

### Version 1.0.0 (C# Implementation)
- Complete C# reimplementation of Python version
- Modern .NET 9 with C# 13 features
- 49+ comprehensive tests
- Full feature parity with Python version
- Improved performance and type safety
