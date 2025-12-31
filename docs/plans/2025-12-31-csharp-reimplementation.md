# C# Re-implementation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Re-implement the Python SimpleNote-to-Obsidian importer in C# using .NET 9 with modern C# syntax and patterns.

**Architecture:** Maintain the existing 4-step pipeline architecture (MetadataParser → ContentProcessor → EditorPipeline → ObsidianFormatter) but use idiomatic C# patterns. Use dependency injection (Microsoft.Extensions.DependencyInjection), primary constructors, record types for DTOs, file-scoped namespaces, and nullable reference types.

**Tech Stack:**
- .NET 9 SDK
- C# 13 (primary constructors, collection expressions, file-scoped namespaces)
- System.CommandLine (CLI parsing)
- YamlDotNet (YAML configuration)
- NUnit (testing framework)
- Shouldly (test assertions)
- Bogus (test data generation)
- NSubstitute (mocking)
- Microsoft.Extensions.DependencyInjection (DI container)
- Microsoft.Extensions.Configuration (configuration system)

---

## Task 1: Archive Python Implementation and Setup C# Project Structure

**Files:**
- Create: `README-CSHARP.md`
- Create: `.gitignore` updates for C#
- Create: `src/ObsidianPorter.sln`
- Create: Directory structure for C# project
- Move: Python files to `python-version/` directory

**Step 1: Archive Python implementation**

Move all Python code to a legacy folder for reference:

```bash
mkdir -p python-version
git mv src python-version/
git mv tests python-version/
git mv import.py python-version/
git mv requirements.txt python-version/
git mv requirements-test.txt python-version/
git mv pytest.ini python-version/
git mv venv python-version/ 2>/dev/null || true
git mv obsidian-porter python-version/ 2>/dev/null || true
git mv PYTHON_GUIDE_FOR_CSHARP_JS_DEVS.md python-version/
```

**Step 2: Create C# .gitignore additions**

Add to `.gitignore`:

```gitignore
# C# / .NET
bin/
obj/
*.user
*.suo
*.cache
.vs/
.vscode/
*.DotSettings.user
TestResults/
*.nupkg
```

**Step 3: Create .NET solution and project structure**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter
dotnet new sln -n ObsidianPorter -o src
dotnet new console -n ObsidianPorter.Cli -o src/ObsidianPorter.Cli -f net9.0
dotnet new classlib -n ObsidianPorter.Core -o src/ObsidianPorter.Core -f net9.0
dotnet new nunit -n ObsidianPorter.Tests -o src/ObsidianPorter.Tests -f net9.0
dotnet sln src/ObsidianPorter.sln add src/ObsidianPorter.Cli/ObsidianPorter.Cli.csproj
dotnet sln src/ObsidianPorter.sln add src/ObsidianPorter.Core/ObsidianPorter.Core.csproj
dotnet sln src/ObsidianPorter.sln add src/ObsidianPorter.Tests/ObsidianPorter.Tests.csproj
```

**Step 4: Add project references**

```bash
cd src
dotnet add ObsidianPorter.Cli/ObsidianPorter.Cli.csproj reference ObsidianPorter.Core/ObsidianPorter.Core.csproj
dotnet add ObsidianPorter.Tests/ObsidianPorter.Tests.csproj reference ObsidianPorter.Core/ObsidianPorter.Core.csproj
```

**Step 5: Install NuGet packages**

```bash
cd ObsidianPorter.Cli
dotnet add package System.CommandLine --version 2.0.0-beta4.22272.1
dotnet add package Microsoft.Extensions.DependencyInjection --version 8.0.0
dotnet add package Microsoft.Extensions.Configuration --version 8.0.0
dotnet add package Microsoft.Extensions.Configuration.Json --version 8.0.0
dotnet add package YamlDotNet --version 15.1.0

cd ../ObsidianPorter.Core
dotnet add package YamlDotNet --version 15.1.0
dotnet add package System.Text.Json --version 9.0.0

cd ../ObsidianPorter.Tests
dotnet add package Shouldly --version 4.2.1
dotnet add package Bogus --version 35.6.1
dotnet add package NSubstitute --version 5.1.0
```

**Step 6: Verify build**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet build
```

Expected: BUILD SUCCEEDED

**Step 7: Create README-CSHARP.md**

Create: `/Users/jhutchinson/Code/Tiberius/obsidian-porter/README-CSHARP.md`

```markdown
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
```

**Step 8: Commit project structure**

```bash
git add .
git commit -m "feat: initialize C# project structure and archive Python implementation"
```

---

## Task 2: Core Interfaces and Models

**Files:**
- Create: `src/ObsidianPorter.Core/Interfaces/IFileSystemService.cs`
- Create: `src/ObsidianPorter.Core/Models/NoteMetadata.cs`
- Create: `src/ObsidianPorter.Core/Models/ImportConfig.cs`
- Create: `src/ObsidianPorter.Core/Models/ProcessedNote.cs`
- Test: `src/ObsidianPorter.Tests/Models/NoteMetadataTests.cs`

**Step 1: Enable nullable reference types and update project settings**

Modify: `src/ObsidianPorter.Core/ObsidianPorter.Core.csproj`

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <LangVersion>13</LangVersion>
  </PropertyGroup>
</Project>
```

**Step 2: Write test for NoteMetadata model**

Create: `src/ObsidianPorter.Tests/Models/NoteMetadataTests.cs`

```csharp
namespace ObsidianPorter.Tests.Models;

using Shouldly;
using ObsidianPorter.Core.Models;

public class NoteMetadataTests
{
    [Test]
    public void Constructor_WithValidData_SetsProperties()
    {
        var created = new DateTime(2024, 1, 1, 12, 0, 0, DateTimeKind.Utc);
        var modified = new DateTime(2024, 1, 2, 12, 0, 0, DateTimeKind.Utc);
        var tags = new[] { "tag1", "tag2" };

        var metadata = new NoteMetadata(
            Title: "Test Note",
            Created: created,
            Modified: modified,
            OriginalId: "abc123",
            Tags: tags,
            IsMarkdown: true,
            IsPinned: false,
            Category: "recipes"
        );

        metadata.Title.ShouldBe("Test Note");
        metadata.Created.ShouldBe(created);
        metadata.Modified.ShouldBe(modified);
        metadata.OriginalId.ShouldBe("abc123");
        metadata.Tags.ShouldBe(tags);
        metadata.IsMarkdown.ShouldBeTrue();
        metadata.IsPinned.ShouldBeFalse();
        metadata.Category.ShouldBe("recipes");
    }

    [Test]
    public void NoteMetadata_WithEmptyTags_ShouldAllowEmptyCollection()
    {
        var metadata = new NoteMetadata(
            Title: "Test",
            Created: DateTime.UtcNow,
            Modified: DateTime.UtcNow,
            OriginalId: "123",
            Tags: [],
            IsMarkdown: false,
            IsPinned: false,
            Category: null
        );

        metadata.Tags.ShouldBeEmpty();
    }
}
```

**Step 3: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~NoteMetadataTests"
```

Expected: FAIL (NoteMetadata type not found)

**Step 4: Implement NoteMetadata record**

Create: `src/ObsidianPorter.Core/Models/NoteMetadata.cs`

```csharp
namespace ObsidianPorter.Core.Models;

/// <summary>
/// Represents metadata for a SimpleNote note.
/// </summary>
/// <param name="Title">The note title (from first line).</param>
/// <param name="Created">Creation timestamp.</param>
/// <param name="Modified">Last modified timestamp.</param>
/// <param name="OriginalId">SimpleNote's original note ID.</param>
/// <param name="Tags">Collection of tags.</param>
/// <param name="IsMarkdown">Whether the note uses markdown formatting.</param>
/// <param name="IsPinned">Whether the note is pinned.</param>
/// <param name="Category">Optional category assigned to the note.</param>
public record NoteMetadata(
    string Title,
    DateTime Created,
    DateTime Modified,
    string OriginalId,
    IReadOnlyList<string> Tags,
    bool IsMarkdown,
    bool IsPinned,
    string? Category
);
```

**Step 5: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~NoteMetadataTests"
```

Expected: PASS

**Step 6: Write test for ProcessedNote model**

Create: `src/ObsidianPorter.Tests/Models/ProcessedNoteTests.cs`

```csharp
namespace ObsidianPorter.Tests.Models;

using Shouldly;
using ObsidianPorter.Core.Models;

public class ProcessedNoteTests
{
    [Test]
    public void Constructor_WithContentAndMetadata_SetsProperties()
    {
        var metadata = new NoteMetadata(
            Title: "Test",
            Created: DateTime.UtcNow,
            Modified: DateTime.UtcNow,
            OriginalId: "123",
            Tags: [],
            IsMarkdown: false,
            IsPinned: false,
            Category: null
        );

        var note = new ProcessedNote(
            Content: "# Test Note\n\nContent here",
            Metadata: metadata,
            Filename: "test-note.txt"
        );

        note.Content.ShouldBe("# Test Note\n\nContent here");
        note.Metadata.ShouldBe(metadata);
        note.Filename.ShouldBe("test-note.txt");
    }
}
```

**Step 7: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ProcessedNoteTests"
```

Expected: FAIL (ProcessedNote type not found)

**Step 8: Implement ProcessedNote record**

Create: `src/ObsidianPorter.Core/Models/ProcessedNote.cs`

```csharp
namespace ObsidianPorter.Core.Models;

/// <summary>
/// Represents a note after content processing.
/// </summary>
/// <param name="Content">The note's text content.</param>
/// <param name="Metadata">The note's metadata.</param>
/// <param name="Filename">The source filename.</param>
public record ProcessedNote(
    string Content,
    NoteMetadata Metadata,
    string Filename
);
```

**Step 9: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ProcessedNoteTests"
```

Expected: PASS

**Step 10: Write test for IFileSystemService interface usage**

Create: `src/ObsidianPorter.Tests/Interfaces/FileSystemServiceTests.cs`

```csharp
namespace ObsidianPorter.Tests.Interfaces;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;

public class FileSystemServiceTests
{
    [Test]
    public void FileExists_WhenFileMissing_ReturnsFalse()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists(Arg.Any<string>()).Returns(false);

        var result = fs.FileExists("/fake/path.txt");

        result.ShouldBeFalse();
    }

    [Test]
    public void ReadAllText_ReturnsFileContent()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.ReadAllText(Arg.Any<string>()).Returns("File content");

        var result = fs.ReadAllText("/fake/file.txt");

        result.ShouldBe("File content");
    }
}
```

**Step 11: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~FileSystemServiceTests"
```

Expected: FAIL (IFileSystemService not found)

**Step 12: Create IFileSystemService interface**

Create: `src/ObsidianPorter.Core/Interfaces/IFileSystemService.cs`

```csharp
namespace ObsidianPorter.Core.Interfaces;

/// <summary>
/// Abstraction for file system operations to enable testing.
/// </summary>
public interface IFileSystemService
{
    bool FileExists(string path);
    bool DirectoryExists(string path);
    string ReadAllText(string path);
    void WriteAllText(string path, string content);
    void CreateDirectory(string path);
    IEnumerable<string> GetFiles(string path, string searchPattern);
    bool IsFile(string path);
    bool IsDirectory(string path);
}
```

**Step 13: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~FileSystemServiceTests"
```

Expected: PASS

**Step 14: Commit models and interfaces**

```bash
git add src/ObsidianPorter.Core/Models/ src/ObsidianPorter.Core/Interfaces/ src/ObsidianPorter.Tests/
git commit -m "feat: add core models and file system interface"
```

---

## Task 3: Configuration System

**Files:**
- Create: `src/ObsidianPorter.Core/Models/ImportConfig.cs`
- Create: `src/ObsidianPorter.Core/Services/ConfigManager.cs`
- Test: `src/ObsidianPorter.Tests/Services/ConfigManagerTests.cs`

**Step 1: Write test for default ImportConfig**

Create: `src/ObsidianPorter.Tests/Models/ImportConfigTests.cs`

```csharp
namespace ObsidianPorter.Tests.Models;

using Shouldly;
using ObsidianPorter.Core.Models;

public class ImportConfigTests
{
    [Test]
    public void DefaultConfig_HasPhase2FeaturesEnabled()
    {
        var config = new ImportConfig();

        config.EnableEditorPipeline.ShouldBeTrue();
        config.EnableAutoTagging.ShouldBeTrue();
        config.EnableFolderOrganization.ShouldBeTrue();
        config.EnableContentTransformation.ShouldBeTrue();
    }

    [Test]
    public void DefaultConfig_HasPhase3FeaturesDisabled()
    {
        var config = new ImportConfig();

        config.EnableNoteSplitting.ShouldBeFalse();
        config.EnableLlmCategorization.ShouldBeFalse();
    }

    [Test]
    public void Categories_DefaultConfig_ContainsExpectedCategories()
    {
        var config = new ImportConfig();

        config.Categories.ShouldContain(c => c.Slug == "cocktails");
        config.Categories.ShouldContain(c => c.Slug == "recipes");
        config.Categories.ShouldContain(c => c.Slug == "other");
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ImportConfigTests"
```

Expected: FAIL (ImportConfig not found)

**Step 3: Implement ImportConfig with primary constructor**

Create: `src/ObsidianPorter.Core/Models/ImportConfig.cs`

```csharp
namespace ObsidianPorter.Core.Models;

/// <summary>
/// Configuration for the import process.
/// </summary>
public class ImportConfig
{
    // Phase 2 Features
    public bool EnableEditorPipeline { get; set; } = true;
    public bool EnableAutoTagging { get; set; } = true;
    public bool EnableFolderOrganization { get; set; } = true;
    public bool EnableContentTransformation { get; set; } = true;

    // Phase 3 Features
    public bool EnableNoteSplitting { get; set; } = false;

    // LLM Categorization
    public bool EnableLlmCategorization { get; set; } = false;
    public string LlmProvider { get; set; } = "openai";
    public string? LlmModel { get; set; }
    public Dictionary<string, string> LlmApiKeys { get; set; } = new();
    public string? LlmBaseUrl { get; set; }
    public int LlmTimeoutSec { get; set; } = 30;
    public int LlmMaxRetries { get; set; } = 2;
    public int LlmConcurrency { get; set; } = 4;
    public bool LlmCacheEnabled { get; set; } = true;
    public string LlmCachePath { get; set; } = ".cache/llm_category.jsonl";
    public double LlmMinConfidence { get; set; } = 0.6;
    public int LlmHeadChars { get; set; } = 2500;
    public int LlmTailChars { get; set; } = 500;
    public string UndecidedPolicy { get; set; } = "suggest";
    public int SuggestionsCount { get; set; } = 3;
    public bool PropagateCategoryTag { get; set; } = true;
    public bool PropagateSuggestedCategoriesWhenOther { get; set; } = true;
    public bool PropagateLlmSuggestedTags { get; set; } = true;
    public string? LlmPromptTemplatePath { get; set; }
    public string LlmPromptVersion { get; set; } = "v1";
    public bool LlmAllowFreeformSuggestions { get; set; } = true;
    public bool LlmSuggestTags { get; set; } = true;
    public int LlmTagsMaxCount { get; set; } = 5;
    public int LlmTagsMinCount { get; set; } = 0;

    public List<CategoryDefinition> Categories { get; set; } = new()
    {
        new("Cocktails", "cocktails", "Cocktail recipes, mixed drinks, ingredients, techniques."),
        new("Recipes", "recipes", "Food recipes, ingredients, cooking instructions."),
        new("Gaming", "gaming", "Video games, gameplay notes, walkthroughs, strategies."),
        new("Music", "music", "Music notes, artists, songs, albums, playlists."),
        new("Track lists", "track-lists", "Tracklists, DJ sets, setlists, ordered lists of tracks."),
        new("House", "house", "Home ownership and maintenance: projects, repairs, appliances, upkeep."),
        new("Role-playing games", "role-playing-games", "Tabletop RPGs, characters, campaigns, rules."),
        new("Cisco", "cisco", "Networking/Cisco notes, configs, commands."),
        new("Other", "other", "Fallback category for low-confidence or uncategorized notes.")
    };

    // Organization Settings
    public bool OrganizeByFolder { get; set; } = true;
    public string FolderStructure { get; set; } = "tags"; // "tags", "date", "custom", "flat"
    public bool CreateIndexFiles { get; set; } = false;

    // Tagging Settings
    public Dictionary<string, List<string>> AutoTagRules { get; set; } = new();
    public List<string> TagBlacklist { get; set; } = new();
    public List<string>? TagWhitelist { get; set; }

    // Content Processing
    public bool CleanWhitespace { get; set; } = true;
    public bool StandardizeHeaders { get; set; } = true;
    public bool FixListFormatting { get; set; } = true;

    // Output Settings
    public string OutputFormat { get; set; } = "obsidian";
    public bool PreserveOriginalStructure { get; set; } = false;
    public bool CreateBacklinks { get; set; } = false;

    // Custom Rules
    public Dictionary<string, List<string>> CustomTagRules { get; set; } = new();
    public Dictionary<string, string> CustomFolderRules { get; set; } = new();
    public Dictionary<string, string> CustomTransformations { get; set; } = new();

    // Note Splitting Settings
    public int SplitHeaderLevel { get; set; } = 2;
    public bool PreserveMainHeader { get; set; } = true;
    public List<string> SplitNotesPatterns { get; set; } = new();
    public List<string> SplitEnabledTags { get; set; } = new() { "cocktails", "recipes", "drinks" };
}

/// <summary>
/// Represents a category definition for LLM-based categorization.
/// </summary>
/// <param name="Name">Display name of the category.</param>
/// <param name="Slug">URL-friendly slug for the category.</param>
/// <param name="Description">Description of what belongs in this category.</param>
public record CategoryDefinition(string Name, string Slug, string Description);
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ImportConfigTests"
```

Expected: PASS

**Step 5: Write test for ConfigManager loading YAML**

Create: `src/ObsidianPorter.Tests/Services/ConfigManagerTests.cs`

```csharp
namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

public class ConfigManagerTests
{
    [Test]
    public void LoadFromFile_WhenFileDoesNotExist_ReturnsDefaultConfig()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists(Arg.Any<string>()).Returns(false);

        var manager = new ConfigManager(fs);
        var config = manager.LoadFromFile("nonexistent.yaml");

        config.ShouldNotBeNull();
        config.EnableEditorPipeline.ShouldBeTrue();
    }

    [Test]
    public void LoadFromFile_WithValidYaml_LoadsConfiguration()
    {
        var yaml = @"
EnableEditorPipeline: false
EnableAutoTagging: true
CleanWhitespace: false
";
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists("test.yaml").Returns(true);
        fs.ReadAllText("test.yaml").Returns(yaml);

        var manager = new ConfigManager(fs);
        var config = manager.LoadFromFile("test.yaml");

        config.EnableEditorPipeline.ShouldBeFalse();
        config.EnableAutoTagging.ShouldBeTrue();
        config.CleanWhitespace.ShouldBeFalse();
    }
}
```

**Step 6: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ConfigManagerTests"
```

Expected: FAIL (ConfigManager not found)

**Step 7: Implement ConfigManager**

Create: `src/ObsidianPorter.Core/Services/ConfigManager.cs`

```csharp
namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

/// <summary>
/// Manages loading and saving of configuration files.
/// </summary>
public class ConfigManager(IFileSystemService fileSystem)
{
    private readonly IFileSystemService _fileSystem = fileSystem;

    public ImportConfig LoadFromFile(string configPath)
    {
        if (!_fileSystem.FileExists(configPath))
        {
            return new ImportConfig();
        }

        try
        {
            var yaml = _fileSystem.ReadAllText(configPath);
            var deserializer = new DeserializerBuilder()
                .WithNamingConvention(PascalCaseNamingConvention.Instance)
                .Build();

            return deserializer.Deserialize<ImportConfig>(yaml) ?? new ImportConfig();
        }
        catch
        {
            return new ImportConfig();
        }
    }

    public void SaveToFile(string configPath, ImportConfig config)
    {
        var serializer = new SerializerBuilder()
            .WithNamingConvention(PascalCaseNamingConvention.Instance)
            .Build();

        var yaml = serializer.Serialize(config);
        _fileSystem.WriteAllText(configPath, yaml);
    }
}
```

**Step 8: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ConfigManagerTests"
```

Expected: PASS

**Step 9: Commit configuration system**

```bash
git add .
git commit -m "feat: add configuration system with YAML support"
```

---

## Task 4: File System Service Implementation

**Files:**
- Create: `src/ObsidianPorter.Core/Services/FileSystemService.cs`
- Test: `src/ObsidianPorter.Tests/Services/FileSystemServiceTests.cs`

**Step 1: Write test for real file system service**

Modify: `src/ObsidianPorter.Tests/Services/FileSystemServiceTests.cs`

Add to existing file:

```csharp
using ObsidianPorter.Core.Services;
using System.IO;

public class FileSystemServiceRealTests : IDisposable
{
    private readonly string _testDir;
    private readonly FileSystemService _fs;

    public FileSystemServiceRealTests()
    {
        _testDir = Path.Combine(Path.GetTempPath(), $"obsidian-porter-test-{Guid.NewGuid()}");
        Directory.CreateDirectory(_testDir);
        _fs = new FileSystemService();
    }

    [Test]
    public void FileExists_WhenFileExists_ReturnsTrue()
    {
        var testFile = Path.Combine(_testDir, "test.txt");
        File.WriteAllText(testFile, "content");

        var result = _fs.FileExists(testFile);

        result.ShouldBeTrue();
    }

    [Test]
    public void ReadAllText_ReturnsFileContent()
    {
        var testFile = Path.Combine(_testDir, "test.txt");
        File.WriteAllText(testFile, "Hello World");

        var content = _fs.ReadAllText(testFile);

        content.ShouldBe("Hello World");
    }

    [Test]
    public void WriteAllText_CreatesFileWithContent()
    {
        var testFile = Path.Combine(_testDir, "output.txt");

        _fs.WriteAllText(testFile, "Test Content");

        File.Exists(testFile).ShouldBeTrue();
        File.ReadAllText(testFile).ShouldBe("Test Content");
    }

    [Test]
    public void GetFiles_ReturnsMatchingFiles()
    {
        File.WriteAllText(Path.Combine(_testDir, "note1.txt"), "");
        File.WriteAllText(Path.Combine(_testDir, "note2.txt"), "");
        File.WriteAllText(Path.Combine(_testDir, "other.md"), "");

        var files = _fs.GetFiles(_testDir, "*.txt");

        files.Count().ShouldBe(2);
        files.ShouldAllBe(f => f.EndsWith(".txt"));
    }

    public void Dispose()
    {
        if (Directory.Exists(_testDir))
        {
            Directory.Delete(_testDir, recursive: true);
        }
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~FileSystemServiceRealTests"
```

Expected: FAIL (FileSystemService not found)

**Step 3: Implement FileSystemService**

Create: `src/ObsidianPorter.Core/Services/FileSystemService.cs`

```csharp
namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;

/// <summary>
/// Real file system implementation.
/// </summary>
public class FileSystemService : IFileSystemService
{
    public bool FileExists(string path) => File.Exists(path);

    public bool DirectoryExists(string path) => Directory.Exists(path);

    public string ReadAllText(string path) => File.ReadAllText(path);

    public void WriteAllText(string path, string content) => File.WriteAllText(path, content);

    public void CreateDirectory(string path) => Directory.CreateDirectory(path);

    public IEnumerable<string> GetFiles(string path, string searchPattern) =>
        Directory.GetFiles(path, searchPattern);

    public bool IsFile(string path) => File.Exists(path) && !Directory.Exists(path);

    public bool IsDirectory(string path) => Directory.Exists(path);
}
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~FileSystemServiceRealTests"
```

Expected: PASS

**Step 5: Commit file system service**

```bash
git add .
git commit -m "feat: implement file system service"
```

---

## Task 5: Metadata Parser

**Files:**
- Create: `src/ObsidianPorter.Core/Services/MetadataParser.cs`
- Test: `src/ObsidianPorter.Tests/Services/MetadataParserTests.cs`

**Step 1: Write test for parsing SimpleNote JSON**

Create: `src/ObsidianPorter.Tests/Services/MetadataParserTests.cs`

```csharp
namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

public class MetadataParserTests
{
    [Test]
    public void Parse_WithValidJson_ReturnsMetadataMap()
    {
        var json = @"
{
  ""activeNotes"": [
    {
      ""id"": ""abc123"",
      ""content"": ""My Test Note\nThis is content"",
      ""creationDate"": ""2024-01-01T12:00:00Z"",
      ""lastModified"": ""2024-01-02T14:30:00Z"",
      ""tags"": [""tag1"", ""tag2""],
      ""systemTags"": [""markdown""],
      ""pinned"": false
    }
  ],
  ""trashedNotes"": []
}
";
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists("notes.json").Returns(true);
        fs.ReadAllText("notes.json").Returns(json);

        var parser = new MetadataParser(fs, "notes.json");
        var result = parser.Parse();

        result.ShouldContainKey("My Test Note.txt");
        var metadata = result["My Test Note.txt"];
        metadata.Title.ShouldBe("My Test Note");
        metadata.OriginalId.ShouldBe("abc123");
        metadata.Tags.ShouldBe(new[] { "tag1", "tag2" });
        metadata.IsMarkdown.ShouldBeTrue();
        metadata.IsPinned.ShouldBeFalse();
    }

    [Test]
    public void Parse_WithMissingFile_ReturnsEmptyDictionary()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists("notes.json").Returns(false);

        var parser = new MetadataParser(fs, "notes.json");
        var result = parser.Parse();

        result.ShouldBeEmpty();
    }

    [Test]
    public void GenerateFilename_SanitizesTitle()
    {
        var fs = Substitute.For<IFileSystemService>();
        var parser = new MetadataParser(fs, "notes.json");

        var filename = parser.GenerateFilename("Test: Note / With \\ Bad * Chars?");

        filename.ShouldBe("Test Note  With  Bad  Chars.txt");
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~MetadataParserTests"
```

Expected: FAIL (MetadataParser not found)

**Step 3: Implement MetadataParser**

Create: `src/ObsidianPorter.Core/Services/MetadataParser.cs`

```csharp
namespace ObsidianPorter.Core.Services;

using System.Text.Json;
using System.Text.RegularExpressions;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Parses metadata from SimpleNote JSON export.
/// </summary>
public partial class MetadataParser(IFileSystemService fileSystem, string jsonPath)
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private readonly string _jsonPath = jsonPath;

    public Dictionary<string, NoteMetadata> Parse()
    {
        if (!_fileSystem.FileExists(_jsonPath))
        {
            return new Dictionary<string, NoteMetadata>();
        }

        try
        {
            var json = _fileSystem.ReadAllText(_jsonPath);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var metadataMap = new Dictionary<string, NoteMetadata>();

            if (root.TryGetProperty("activeNotes", out var activeNotes))
            {
                foreach (var note in activeNotes.EnumerateArray())
                {
                    var metadata = ParseNote(note);
                    var filename = GenerateFilename(metadata.Title);
                    metadataMap[filename] = metadata;
                }
            }

            return metadataMap;
        }
        catch
        {
            return new Dictionary<string, NoteMetadata>();
        }
    }

    private static NoteMetadata ParseNote(JsonElement note)
    {
        var content = note.GetProperty("content").GetString() ?? "";
        var title = ExtractTitle(content);
        var id = note.GetProperty("id").GetString() ?? "";
        var created = DateTime.Parse(note.GetProperty("creationDate").GetString() ?? DateTime.UtcNow.ToString());
        var modified = DateTime.Parse(note.GetProperty("lastModified").GetString() ?? DateTime.UtcNow.ToString());

        var tags = new List<string>();
        if (note.TryGetProperty("tags", out var tagsElement))
        {
            tags = tagsElement.EnumerateArray().Select(t => t.GetString() ?? "").ToList();
        }

        var isMarkdown = false;
        if (note.TryGetProperty("systemTags", out var systemTags))
        {
            isMarkdown = systemTags.EnumerateArray().Any(t => t.GetString() == "markdown");
        }

        var isPinned = note.TryGetProperty("pinned", out var pinnedElement) && pinnedElement.GetBoolean();

        return new NoteMetadata(
            Title: title,
            Created: created,
            Modified: modified,
            OriginalId: id,
            Tags: tags,
            IsMarkdown: isMarkdown,
            IsPinned: isPinned,
            Category: null
        );
    }

    private static string ExtractTitle(string content)
    {
        var lines = content.Split('\n');
        return lines.Length > 0 ? lines[0].Trim() : "Untitled";
    }

    public string GenerateFilename(string title)
    {
        // Remove invalid filename characters
        var sanitized = InvalidFileNameCharsRegex().Replace(title, " ");
        sanitized = sanitized.Trim();

        if (string.IsNullOrWhiteSpace(sanitized))
        {
            sanitized = "Untitled";
        }

        return sanitized + ".txt";
    }

    [GeneratedRegex(@"[<>:""/\\|?*]")]
    private static partial Regex InvalidFileNameCharsRegex();
}
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~MetadataParserTests"
```

Expected: PASS

**Step 5: Commit metadata parser**

```bash
git add .
git commit -m "feat: implement metadata parser for SimpleNote JSON"
```

---

## Task 6: Content Processor

**Files:**
- Create: `src/ObsidianPorter.Core/Services/ContentProcessor.cs`
- Test: `src/ObsidianPorter.Tests/Services/ContentProcessorTests.cs`

**Step 1: Write test for content processing**

Create: `src/ObsidianPorter.Tests/Services/ContentProcessorTests.cs`

```csharp
namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

public class ContentProcessorTests
{
    [Test]
    public void ProcessAllNotes_FindsAndProcessesTxtFiles()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.DirectoryExists("/notes").Returns(true);
        fs.GetFiles("/notes", "*.txt").Returns(new[] { "/notes/note1.txt", "/notes/note2.txt" });
        fs.ReadAllText("/notes/note1.txt").Returns("First Note\nContent here");
        fs.ReadAllText("/notes/note2.txt").Returns("Second Note\nMore content");

        var processor = new ContentProcessor(fs, "/notes");
        var notes = processor.ProcessAllNotes();

        notes.Count.ShouldBe(2);
        notes[0].Content.ShouldContain("First Note");
        notes[1].Content.ShouldContain("Second Note");
    }

    [Test]
    public void ProcessAllNotes_WhenNoFiles_ReturnsEmpty()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.DirectoryExists("/notes").Returns(true);
        fs.GetFiles("/notes", "*.txt").Returns(Array.Empty<string>());

        var processor = new ContentProcessor(fs, "/notes");
        var notes = processor.ProcessAllNotes();

        notes.ShouldBeEmpty();
    }

    [Test]
    public void ExtractTitle_FromFirstLine_ReturnsTitle()
    {
        var fs = Substitute.For<IFileSystemService>();
        var processor = new ContentProcessor(fs, "/notes");

        var title = processor.ExtractTitle("My Note Title\nContent here\nMore content");

        title.ShouldBe("My Note Title");
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ContentProcessorTests"
```

Expected: FAIL (ContentProcessor not found)

**Step 3: Implement ContentProcessor**

Create: `src/ObsidianPorter.Core/Services/ContentProcessor.cs`

```csharp
namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Processes SimpleNote .txt files.
/// </summary>
public class ContentProcessor(IFileSystemService fileSystem, string notesDirectory)
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private readonly string _notesDirectory = notesDirectory;

    public List<ProcessedNote> ProcessAllNotes()
    {
        if (!_fileSystem.DirectoryExists(_notesDirectory))
        {
            return new List<ProcessedNote>();
        }

        var txtFiles = _fileSystem.GetFiles(_notesDirectory, "*.txt");
        var notes = new List<ProcessedNote>();

        foreach (var filePath in txtFiles)
        {
            try
            {
                var content = _fileSystem.ReadAllText(filePath);
                var title = ExtractTitle(content);
                var filename = Path.GetFileName(filePath);

                // Create basic metadata (will be enriched by MetadataParser if available)
                var metadata = new NoteMetadata(
                    Title: title,
                    Created: DateTime.UtcNow,
                    Modified: DateTime.UtcNow,
                    OriginalId: "",
                    Tags: Array.Empty<string>(),
                    IsMarkdown: false,
                    IsPinned: false,
                    Category: null
                );

                notes.Add(new ProcessedNote(content, metadata, filename));
            }
            catch
            {
                // Skip files that can't be read
                continue;
            }
        }

        return notes;
    }

    public string ExtractTitle(string content)
    {
        var lines = content.Split('\n');
        if (lines.Length == 0 || string.IsNullOrWhiteSpace(lines[0]))
        {
            return "Untitled";
        }

        return lines[0].Trim();
    }
}
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~ContentProcessorTests"
```

Expected: PASS

**Step 5: Commit content processor**

```bash
git add .
git commit -m "feat: implement content processor for .txt files"
```

---

## Task 7: Pipeline Base Processor Interface

**Files:**
- Create: `src/ObsidianPorter.Core/Interfaces/IContentProcessor.cs`
- Create: `src/ObsidianPorter.Core/Pipelines/BaseContentProcessor.cs`
- Test: `src/ObsidianPorter.Tests/Pipelines/BaseContentProcessorTests.cs`

**Step 1: Write test for base processor**

Create: `src/ObsidianPorter.Tests/Pipelines/BaseContentProcessorTests.cs`

```csharp
namespace ObsidianPorter.Tests.Pipelines;

using Shouldly;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Pipelines;

public class BaseContentProcessorTests
{
    private class TestProcessor : BaseContentProcessor
    {
        public override string Name => "test_processor";

        public override (string Content, NoteMetadata Metadata) Process(
            string content,
            NoteMetadata metadata,
            Dictionary<string, object> context)
        {
            var updated = metadata with { Tags = metadata.Tags.Append("processed").ToList() };
            return (content.ToUpper(), updated);
        }
    }

    [Test]
    public void Process_ModifiesContentAndMetadata()
    {
        var processor = new TestProcessor();
        var metadata = new NoteMetadata(
            Title: "Test",
            Created: DateTime.UtcNow,
            Modified: DateTime.UtcNow,
            OriginalId: "123",
            Tags: new List<string> { "original" },
            IsMarkdown: false,
            IsPinned: false,
            Category: null
        );

        var (newContent, newMetadata) = processor.Process(
            "hello world",
            metadata,
            new Dictionary<string, object>()
        );

        newContent.ShouldBe("HELLO WORLD");
        newMetadata.Tags.ShouldContain("processed");
        newMetadata.Tags.ShouldContain("original");
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~BaseContentProcessorTests"
```

Expected: FAIL (BaseContentProcessor not found)

**Step 3: Create IContentProcessor interface**

Create: `src/ObsidianPorter.Core/Interfaces/IContentProcessor.cs`

```csharp
namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Interface for content processing pipeline components.
/// </summary>
public interface IContentProcessor
{
    string Name { get; }

    (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context);

    bool ShouldProcess(NoteMetadata metadata, Dictionary<string, object> context);
}
```

**Step 4: Implement BaseContentProcessor**

Create: `src/ObsidianPorter.Core/Pipelines/BaseContentProcessor.cs`

```csharp
namespace ObsidianPorter.Core.Pipelines;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Base class for content processors in the editor pipeline.
/// </summary>
public abstract class BaseContentProcessor : IContentProcessor
{
    public abstract string Name { get; }

    public abstract (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context);

    public virtual bool ShouldProcess(NoteMetadata metadata, Dictionary<string, object> context)
    {
        return true; // Process by default
    }
}
```

**Step 5: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~BaseContentProcessorTests"
```

Expected: PASS

**Step 6: Commit base processor**

```bash
git add .
git commit -m "feat: add base content processor interface and abstract class"
```

---

## Task 8: Tag Injector Pipeline Processor

**Files:**
- Create: `src/ObsidianPorter.Core/Pipelines/TagInjector.cs`
- Test: `src/ObsidianPorter.Tests/Pipelines/TagInjectorTests.cs`

**Step 1: Write test for TagInjector**

Create: `src/ObsidianPorter.Tests/Pipelines/TagInjectorTests.cs`

```csharp
namespace ObsidianPorter.Tests.Pipelines;

using Shouldly;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Pipelines;

public class TagInjectorTests
{
    [Test]
    public void Process_WithListContent_AddsListTag()
    {
        var injector = new TagInjector(new Dictionary<string, List<string>>(), true);
        var content = @"Shopping List
- Milk
- Bread
- Eggs
- Cheese";
        var metadata = CreateBasicMetadata();

        var (_, updatedMetadata) = injector.Process(content, metadata, new Dictionary<string, object>
        {
            { "filename", "shopping.txt" }
        });

        updatedMetadata.Tags.ShouldContain("lists");
    }

    [Test]
    public void Process_WithCategoryInMetadata_PropagatesCategoryTag()
    {
        var injector = new TagInjector(new Dictionary<string, List<string>>(), propagateCategoryTag: true);
        var metadata = CreateBasicMetadata() with { Category = "recipes" };

        var (_, updatedMetadata) = injector.Process("content", metadata, new Dictionary<string, object>
        {
            { "filename", "test.txt" }
        });

        updatedMetadata.Tags.ShouldContain("recipes");
    }

    [Test]
    public void Process_WithCustomRules_AppliesTagsWhenPatternMatches()
    {
        var rules = new Dictionary<string, List<string>>
        {
            { "cocktail|drink|recipe", new List<string> { "cocktails", "beverages" } }
        };
        var injector = new TagInjector(rules, false);
        var content = "Old Fashioned cocktail recipe";
        var metadata = CreateBasicMetadata();

        var (_, updatedMetadata) = injector.Process(content, metadata, new Dictionary<string, object>
        {
            { "filename", "test.txt" }
        });

        updatedMetadata.Tags.ShouldContain("cocktails");
        updatedMetadata.Tags.ShouldContain("beverages");
    }

    private static NoteMetadata CreateBasicMetadata() =>
        new(
            Title: "Test",
            Created: DateTime.UtcNow,
            Modified: DateTime.UtcNow,
            OriginalId: "123",
            Tags: new List<string>(),
            IsMarkdown: false,
            IsPinned: false,
            Category: null
        );
}
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~TagInjectorTests"
```

Expected: FAIL (TagInjector not found)

**Step 3: Implement TagInjector**

Create: `src/ObsidianPorter.Core/Pipelines/TagInjector.cs`

```csharp
namespace ObsidianPorter.Core.Pipelines;

using System.Text.RegularExpressions;
using ObsidianPorter.Core.Models;

/// <summary>
/// Adds tags based on content analysis and filename patterns.
/// </summary>
public partial class TagInjector(
    Dictionary<string, List<string>> tagRules,
    bool propagateCategoryTag) : BaseContentProcessor
{
    private readonly Dictionary<string, List<string>> _tagRules = tagRules;
    private readonly bool _propagateCategoryTag = propagateCategoryTag;

    public override string Name => "tag_injector";

    public override (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context)
    {
        var newTags = new HashSet<string>(metadata.Tags);

        // Extract tags from filename
        var filename = context.TryGetValue("filename", out var fn) ? fn?.ToString() ?? "" : "";
        newTags.UnionWith(ExtractFilenameTagsInternal(filename));

        // Extract tags from content
        newTags.UnionWith(ExtractContentTags(content));

        // Propagate category tag if configured
        if (_propagateCategoryTag && metadata.Category is not null)
        {
            newTags.Add(metadata.Category);
        }

        var updatedMetadata = metadata with { Tags = newTags.OrderBy(t => t).ToList() };
        return (content, updatedMetadata);
    }

    private List<string> ExtractFilenameTagsInternal(string filename)
    {
        var tags = new List<string>();

        // Check for date patterns (journal entries)
        if (DatePatternRegex().IsMatch(filename))
        {
            tags.Add("journal");
        }

        // Check for specific prefixes
        if (filename.StartsWith('#'))
        {
            tags.Add("reference");
        }

        // Apply custom rules
        var filenameLower = filename.ToLowerInvariant();
        foreach (var (pattern, patternTags) in _tagRules)
        {
            if (Regex.IsMatch(filenameLower, pattern, RegexOptions.IgnoreCase))
            {
                tags.AddRange(patternTags);
            }
        }

        return tags;
    }

    private List<string> ExtractContentTags(string content)
    {
        var tags = new List<string>();
        var contentLower = content.ToLowerInvariant();

        // Apply custom rules
        foreach (var (pattern, patternTags) in _tagRules)
        {
            if (Regex.IsMatch(contentLower, pattern, RegexOptions.IgnoreCase))
            {
                tags.AddRange(patternTags);
            }
        }

        // Check for list patterns
        var lines = content.Split('\n');
        var listLines = lines.Count(line =>
            line.TrimStart().StartsWith("- ") ||
            line.TrimStart().StartsWith("* ") ||
            line.TrimStart().StartsWith("+ ") ||
            Regex.IsMatch(line, @"^\s*\d+\.\s"));

        if (listLines > 3)
        {
            tags.Add("lists");
        }

        return tags;
    }

    [GeneratedRegex(@"\d{2}-\d{2}-\d{4}")]
    private static partial Regex DatePatternRegex();
}
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/jhutchinson/Code/Tiberius/obsidian-porter/src
dotnet test --filter "FullyQualifiedName~TagInjectorTests"
```

Expected: PASS

**Step 5: Commit tag injector**

```bash
git add .
git commit -m "feat: implement tag injector pipeline processor"
```

---

## Task 9: Continue with Remaining Pipeline Processors

Due to length constraints, I'll outline the remaining tasks at a high level. Each would follow the same TDD pattern:

**Task 9: Content Transformer**
- Test → Implement whitespace cleaning, header standardization, list formatting
- File: `src/ObsidianPorter.Core/Pipelines/ContentTransformer.cs`

**Task 10: Folder Organizer**
- Test → Implement content-based folder assignment
- File: `src/ObsidianPorter.Core/Pipelines/FolderOrganizer.cs`

**Task 11: Editor Pipeline**
- Test → Implement pipeline orchestrator that runs processors in sequence
- File: `src/ObsidianPorter.Core/Services/EditorPipeline.cs`

**Task 12: Obsidian Formatter**
- Test → Implement YAML frontmatter generation and filename sanitization
- File: `src/ObsidianPorter.Core/Services/ObsidianFormatter.cs`

**Task 13: Main Importer Orchestrator**
- Test → Implement SimpleNoteImporter that coordinates all components
- File: `src/ObsidianPorter.Core/Services/SimpleNoteImporter.cs`

**Task 14: CLI Application**
- Test → Implement command-line interface with System.CommandLine
- File: `src/ObsidianPorter.Cli/Program.cs`

**Task 15: Integration Tests**
- Test full pipeline end-to-end
- File: `src/ObsidianPorter.Tests/Integration/FullPipelineTests.cs`

**Task 16: Documentation**
- Update README-CSHARP.md with full usage examples
- Create appsettings.json example
- Document configuration options

**Task 17: Final Testing and Verification**
- Run full test suite
- Test with actual SimpleNote export data
- Compare output with Python version

---

## Notes for C# Implementation

### Modern C# Features to Use

1. **Primary Constructors**: Used for dependency injection
   ```csharp
   public class MetadataParser(IFileSystemService fs, string path)
   ```

2. **File-Scoped Namespaces**: Use throughout
   ```csharp
   namespace ObsidianPorter.Core.Services;
   ```

3. **Record Types**: For immutable DTOs
   ```csharp
   public record NoteMetadata(...)
   ```

4. **Collection Expressions**: For array/list initialization
   ```csharp
   Tags: []
   ```

5. **Nullable Reference Types**: Enabled in all projects

6. **Pattern Matching**: Use in switch expressions and is patterns

7. **LINQ**: For data transformations

### Testing Strategy

- Use NUnit for all tests
- Shouldly for readable assertions
- Bogus for generating test data (when needed for complex scenarios)
- NSubstitute for mocking
- Test file system operations with in-memory mock
- Aim for >90% code coverage
- Integration tests for full pipeline

### Dependency Injection

Use Microsoft.Extensions.DependencyInjection:
```csharp
services.AddSingleton<IFileSystemService, FileSystemService>();
services.AddTransient<MetadataParser>();
services.AddTransient<ContentProcessor>();
// etc.
```

### Configuration

- Use appsettings.json for default config
- Support YAML config files via YamlDotNet
- CLI arguments override config file settings

---

## Execution Recommendations

This plan is designed for Test-Driven Development with frequent commits. Each task follows:
1. Write failing test
2. Implement minimal code
3. Verify test passes
4. Commit

The plan maintains the Python architecture but uses idiomatic C# patterns throughout.
