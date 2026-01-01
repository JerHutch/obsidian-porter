# Dependency Injection Refactoring Design

**Date:** 2026-01-01
**Status:** Approved
**Goal:** Refactor C# implementation to use dependency injection throughout, making the codebase more testable and maintainable.

## Overview

This design adds comprehensive dependency injection to the ObsidianPorter C# application. Currently, services are instantiated directly with constructors that take both dependencies and runtime parameters (paths, configs). We'll introduce interfaces for all services, register them with Microsoft.Extensions.DependencyInjection, and use a factory pattern to handle runtime parameters.

## Key Design Decisions

### Service Lifetimes
- **Singleton:** `IConfigManager` - Holds state for current import operation
- **Scoped:** All other services - New instances per import operation
  - `IFileSystemService`
  - `IMetadataParser`
  - `IContentProcessor`
  - `IObsidianFormatter`
  - `ISimpleNoteImporter`
  - `ISimpleNoteImporterFactory`

### Configuration Strategy
- `IConfigManager` becomes stateful with `SetCurrentConfig()` and getter methods
- All services receive `IConfigManager` instead of individual path parameters
- Factory sets configuration before creating services
- Eliminates passing paths through constructors

### Factory Pattern
- `ISimpleNoteImporterFactory` creates `ISimpleNoteImporter` instances with runtime parameters
- Factory injected into `Program.cs` to create importers
- Factory sets config in `ConfigManager` before resolving services from DI

## Interface Definitions

### New Interfaces

All interfaces will be placed in `ObsidianPorter.Core/Interfaces/`.

#### IConfigManager
```csharp
public interface IConfigManager
{
    ImportConfig LoadFromFile(string configPath);
    void SaveToFile(string configPath, ImportConfig config);

    // Current configuration state
    void SetCurrentConfig(ImportConfig config, string notesDirectory, string jsonPath, string outputDirectory);
    ImportConfig GetConfig();
    string GetNotesDirectory();
    string GetJsonPath();
    string GetOutputDirectory();
}
```

#### IMetadataParser
```csharp
public interface IMetadataParser
{
    Dictionary<string, NoteMetadata> Parse();
}
```

#### IContentProcessor
```csharp
// Note: Rename to IContentProcessorService to avoid conflict with pipeline IContentProcessor
public interface IContentProcessorService
{
    List<ProcessedNote> ProcessAllNotes();
    string ExtractTitle(string content);
}
```

#### IObsidianFormatter
```csharp
public interface IObsidianFormatter
{
    void FormatAndSave(string content, NoteMetadata metadata, Dictionary<string, object> context);
}
```

#### ISimpleNoteImporter
```csharp
public interface ISimpleNoteImporter
{
    ImportResult Import();
}
```

#### ISimpleNoteImporterFactory
```csharp
public interface ISimpleNoteImporterFactory
{
    ISimpleNoteImporter Create(
        ImportConfig config,
        string notesDirectory,
        string jsonPath,
        string outputDirectory);
}
```

## Service Registration

Create `ObsidianPorter.Core/ServiceCollectionExtensions.cs`:

```csharp
using Microsoft.Extensions.DependencyInjection;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

namespace ObsidianPorter.Core;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddObsidianPorterServices(this IServiceCollection services)
    {
        // Singleton - ConfigManager holds state for current import operation
        services.AddSingleton<IConfigManager, ConfigManager>();

        // Scoped - New instances per import operation (per scope)
        services.AddScoped<IFileSystemService, FileSystemService>();
        services.AddScoped<IMetadataParser, MetadataParser>();
        services.AddScoped<IContentProcessorService, ContentProcessor>();
        services.AddScoped<IObsidianFormatter, ObsidianFormatter>();
        services.AddScoped<ISimpleNoteImporter, SimpleNoteImporter>();
        services.AddScoped<ISimpleNoteImporterFactory, SimpleNoteImporterFactory>();

        return services;
    }
}
```

## Service Implementation Changes

### ConfigManager

Add state management methods:

```csharp
public class ConfigManager : IConfigManager
{
    private readonly IFileSystemService _fileSystem;
    private ImportConfig? _currentConfig;
    private string? _notesDirectory;
    private string? _jsonPath;
    private string? _outputDirectory;

    public void SetCurrentConfig(
        ImportConfig config,
        string notesDirectory,
        string jsonPath,
        string outputDirectory)
    {
        _currentConfig = config;
        _notesDirectory = notesDirectory;
        _jsonPath = jsonPath;
        _outputDirectory = outputDirectory;
    }

    public ImportConfig GetConfig()
        => _currentConfig ?? throw new InvalidOperationException("Config not set");

    public string GetNotesDirectory()
        => _notesDirectory ?? throw new InvalidOperationException("Notes directory not set");

    public string GetJsonPath()
        => _jsonPath ?? throw new InvalidOperationException("JSON path not set");

    public string GetOutputDirectory()
        => _outputDirectory ?? throw new InvalidOperationException("Output directory not set");

    // Existing methods remain unchanged
}
```

### Service Constructors

Update all service constructors to take `IConfigManager`:

```csharp
// MetadataParser
public MetadataParser(IFileSystemService fileSystem, IConfigManager configManager)
{
    _fileSystem = fileSystem;
    _jsonPath = configManager.GetJsonPath();
}

// ContentProcessor
public ContentProcessor(IFileSystemService fileSystem, IConfigManager configManager)
{
    _fileSystem = fileSystem;
    _notesDirectory = configManager.GetNotesDirectory();
}

// ObsidianFormatter
public ObsidianFormatter(IFileSystemService fileSystem, IConfigManager configManager)
{
    _fileSystem = fileSystem;
    _outputDirectory = configManager.GetOutputDirectory();
}
```

### SimpleNoteImporter

Remove path parameters, inject all services:

```csharp
public class SimpleNoteImporter : ISimpleNoteImporter
{
    private readonly IFileSystemService _fileSystem;
    private readonly IConfigManager _configManager;
    private readonly IMetadataParser _metadataParser;
    private readonly IContentProcessorService _contentProcessor;
    private readonly IObsidianFormatter _formatter;

    public SimpleNoteImporter(
        IFileSystemService fileSystem,
        IConfigManager configManager,
        IMetadataParser metadataParser,
        IContentProcessorService contentProcessor,
        IObsidianFormatter formatter)
    {
        _fileSystem = fileSystem;
        _configManager = configManager;
        _metadataParser = metadataParser;
        _contentProcessor = contentProcessor;
        _formatter = formatter;
    }

    public ImportResult Import()
    {
        var config = _configManager.GetConfig();

        // Parse metadata
        var metadataMap = _metadataParser.Parse();

        // Process content
        var processedNotes = _contentProcessor.ProcessAllNotes();

        // Merge and process...
        // Existing logic remains the same
    }
}
```

### SimpleNoteImporterFactory

Create factory that resolves from DI:

```csharp
using Microsoft.Extensions.DependencyInjection;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

namespace ObsidianPorter.Core.Services;

public class SimpleNoteImporterFactory : ISimpleNoteImporterFactory
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IConfigManager _configManager;

    public SimpleNoteImporterFactory(
        IServiceProvider serviceProvider,
        IConfigManager configManager)
    {
        _serviceProvider = serviceProvider;
        _configManager = configManager;
    }

    public ISimpleNoteImporter Create(
        ImportConfig config,
        string notesDirectory,
        string jsonPath,
        string outputDirectory)
    {
        // Set configuration state
        _configManager.SetCurrentConfig(config, notesDirectory, jsonPath, outputDirectory);

        // Resolve importer from DI (all dependencies injected automatically)
        return _serviceProvider.GetRequiredService<ISimpleNoteImporter>();
    }
}
```

## Program.cs Integration

Update CLI entry point to use DI:

```csharp
using System.CommandLine;
using Microsoft.Extensions.DependencyInjection;
using ObsidianPorter.Core;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

// Build DI container at startup
var services = new ServiceCollection();
services.AddObsidianPorterServices();
var serviceProvider = services.BuildServiceProvider();

var rootCommand = new RootCommand("SimpleNote to Obsidian Importer...");

// ... option definitions unchanged ...

rootCommand.SetHandler((string notesDir, string jsonPath, string outputDir, string? configPath, bool smart) =>
{
    try
    {
        Console.WriteLine("SimpleNote to Obsidian Importer");
        Console.WriteLine("================================\n");

        // Create scope for this import operation
        using var scope = serviceProvider.CreateScope();
        var scopedServices = scope.ServiceProvider;

        // Resolve services from DI
        var configManager = scopedServices.GetRequiredService<IConfigManager>();
        var importerFactory = scopedServices.GetRequiredService<ISimpleNoteImporterFactory>();

        // Load configuration
        var config = LoadConfiguration(configManager, configPath, smart);

        Console.WriteLine($"Notes directory: {notesDir}");
        Console.WriteLine($"JSON metadata: {jsonPath}");
        Console.WriteLine($"Output directory: {outputDir}");
        Console.WriteLine($"Smart processing: {(config.EnableEditorPipeline ? "enabled" : "disabled")}\n");

        // Create importer via factory
        var importer = importerFactory.Create(config, notesDir, jsonPath, outputDir);

        Console.WriteLine("Starting import...\n");
        var result = importer.Import();

        // Display results (unchanged)
        Console.WriteLine("\nImport Complete!");
        Console.WriteLine("================");
        Console.WriteLine($"Total notes processed: {result.TotalNotes}");
        Console.WriteLine($"Successfully imported: {result.SuccessfulNotes}");
        Console.WriteLine($"Failed: {result.FailedNotes}");

        if (result.FailedNotes > 0)
        {
            Console.WriteLine("\nWarning: Some notes failed to import.");
        }

        Console.WriteLine($"\nOutput written to: {Path.GetFullPath(outputDir)}");
    }
    catch (Exception ex)
    {
        Console.Error.WriteLine($"\nError: {ex.Message}");
        Console.Error.WriteLine($"\nStack trace:\n{ex.StackTrace}");
        Environment.Exit(1);
    }
}, notesOption, jsonOption, outputOption, configOption, smartOption);

return await rootCommand.InvokeAsync(args);

static ImportConfig LoadConfiguration(IConfigManager configManager, string? configPath, bool smart)
{
    ImportConfig config;

    if (!string.IsNullOrWhiteSpace(configPath))
    {
        config = configManager.LoadFromFile(configPath);
        Console.WriteLine($"Configuration loaded from: {configPath}");
    }
    else if (smart)
    {
        config = new ImportConfig
        {
            EnableEditorPipeline = true,
            EnableAutoTagging = true,
            EnableFolderOrganization = true,
            EnableContentTransformation = true
        };
        Console.WriteLine("Using default smart configuration");
    }
    else
    {
        config = new ImportConfig
        {
            EnableEditorPipeline = false
        };
        Console.WriteLine("Using minimal configuration (Phase 1 compatibility)");
    }

    return config;
}
```

## Testing Strategy

### Unit Tests

Mock all interfaces for isolated testing:

```csharp
// Before
var mockFileSystem = new Mock<IFileSystemService>();
var parser = new MetadataParser(mockFileSystem.Object, "/path/to/json");

// After
var mockFileSystem = new Mock<IFileSystemService>();
var mockConfigManager = new Mock<IConfigManager>();
mockConfigManager.Setup(c => c.GetJsonPath()).Returns("/path/to/json");

var parser = new MetadataParser(mockFileSystem.Object, mockConfigManager.Object);
```

### Integration Tests

Use real DI container with test implementations:

```csharp
var services = new ServiceCollection();
services.AddObsidianPorterServices();

// Override with test implementations
services.AddSingleton<IFileSystemService, InMemoryFileSystemService>();

var serviceProvider = services.BuildServiceProvider();
using var scope = serviceProvider.CreateScope();

// Test complete pipeline with real DI resolution
```

### Test Updates Required

1. Update all service constructor calls to include `IConfigManager`
2. Mock `IConfigManager` methods in addition to file system
3. Use interface types instead of concrete classes
4. Existing test coverage and structure remains unchanged

## Implementation Checklist

- [ ] Create all interface files in `ObsidianPorter.Core/Interfaces/`
- [ ] Rename existing `IContentProcessor` usage to avoid conflicts
- [ ] Update `ConfigManager` with state management methods
- [ ] Update service constructors to accept `IConfigManager`
- [ ] Create `SimpleNoteImporterFactory` class
- [ ] Create `ServiceCollectionExtensions` class
- [ ] Update `Program.cs` to use DI container
- [ ] Add `Microsoft.Extensions.DependencyInjection` NuGet package to CLI project
- [ ] Update all unit tests to use new interfaces
- [ ] Update integration tests to use DI container
- [ ] Run full test suite to verify functionality
- [ ] Update documentation/README if needed

## Dependencies

- `Microsoft.Extensions.DependencyInjection` - Already available in .NET 9

## Benefits

1. **Testability:** All dependencies can be mocked via interfaces
2. **Maintainability:** Clear separation of concerns and dependencies
3. **Flexibility:** Easy to swap implementations (e.g., different file systems)
4. **Consistency:** Standard .NET DI patterns throughout application
5. **Lifetime Management:** Proper scoping of services per import operation

## Backward Compatibility

All existing functionality remains unchanged. This is purely an architectural refactoring with no changes to:
- CLI interface
- Configuration format
- Import behavior
- Output format
