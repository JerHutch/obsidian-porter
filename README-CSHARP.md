# SimpleNote to Obsidian Importer (C# Edition)

A .NET 9 tool for converting SimpleNote exports to Obsidian-compatible markdown files.

## Requirements
- .NET 9 SDK

## Building
```bash
cd src
dotnet build
```

## Running
```bash
cd src/ObsidianPorter.Cli
dotnet run -- --notes data --json data/source/notes.json
```

## Testing
```bash
cd src
dotnet test
```

## Legacy Python Implementation
The original Python implementation is available in the `python-version/` directory for reference.
