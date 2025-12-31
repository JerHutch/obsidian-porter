namespace ObsidianPorter.Tests.Integration;

using Shouldly;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Services;
using System.IO;

public class FullPipelineIntegrationTests : IDisposable
{
    private readonly string _testDir;
    private readonly string _notesDir;
    private readonly string _sourceDir;
    private readonly string _outputDir;
    private readonly FileSystemService _fs;

    public FullPipelineIntegrationTests()
    {
        _testDir = Path.Combine(Path.GetTempPath(), $"obsidian-porter-test-{Guid.NewGuid()}");
        _notesDir = Path.Combine(_testDir, "notes");
        _sourceDir = Path.Combine(_notesDir, "source");
        _outputDir = Path.Combine(_testDir, "output");
        _fs = new FileSystemService();

        // Create test directories
        Directory.CreateDirectory(_notesDir);
        Directory.CreateDirectory(_sourceDir);
    }

    [Test]
    public void EndToEnd_WithBasicConfiguration_ImportsAllNotes()
    {
        // Arrange - Create test data
        CreateTestData();

        var config = new ImportConfig
        {
            EnableEditorPipeline = false
        };

        // Act - Run import
        var importer = new SimpleNoteImporter(
            _fs,
            config,
            _notesDir,
            Path.Combine(_sourceDir, "notes.json"),
            _outputDir
        );

        var result = importer.Import();

        // Assert
        result.TotalNotes.ShouldBe(2);
        result.SuccessfulNotes.ShouldBe(2);
        result.FailedNotes.ShouldBe(0);

        // Verify output files exist
        var outputFiles = Directory.GetFiles(_outputDir, "*.md", SearchOption.AllDirectories);
        outputFiles.Length.ShouldBe(2);

        // Verify content
        var note1Path = Path.Combine(_outputDir, "Test Note 1.md");
        File.Exists(note1Path).ShouldBeTrue();

        var note1Content = File.ReadAllText(note1Path);
        note1Content.ShouldContain("---");
        note1Content.ShouldContain("title: \"Test Note 1\"");
        note1Content.ShouldContain("source: \"simplenote\"");
        note1Content.ShouldContain("Content for note 1");
    }

    [Test]
    public void EndToEnd_WithSmartProcessing_AppliesAllTransformations()
    {
        // Arrange - Clean and create test data with messy formatting
        CleanTestDirectory();
        CreateTestDataWithMessyFormatting();

        var config = new ImportConfig
        {
            EnableEditorPipeline = true,
            EnableAutoTagging = true,
            EnableFolderOrganization = true,
            EnableContentTransformation = true,
            CleanWhitespace = true,
            StandardizeHeaders = true,
            FixListFormatting = true,
            PropagateCategoryTag = false
        };

        // Act
        var importer = new SimpleNoteImporter(
            _fs,
            config,
            _notesDir,
            Path.Combine(_sourceDir, "notes.json"),
            _outputDir
        );

        var result = importer.Import();

        // Assert
        result.SuccessfulNotes.ShouldBe(1);

        // Verify transformations were applied
        var outputFiles = Directory.GetFiles(_outputDir, "*.md", SearchOption.AllDirectories);
        outputFiles.Length.ShouldBe(1);

        var content = File.ReadAllText(outputFiles[0]);

        // Content transformation applied (whitespace cleaned)
        content.ShouldNotContain("  \n");  // No trailing spaces

        // Headers standardized
        content.ShouldContain("# Header");
        content.ShouldNotContain("#Header");

        // Lists fixed
        content.ShouldContain("- Item 1");
        content.ShouldNotContain("-Item 1");
    }

    [Test]
    public void EndToEnd_WithFolderOrganization_CreatesSubfolders()
    {
        // Arrange - Clean and create test data
        CleanTestDirectory();
        CreateTestDataWithTags();

        var config = new ImportConfig
        {
            EnableEditorPipeline = true,
            EnableAutoTagging = false,
            EnableFolderOrganization = true,
            EnableContentTransformation = false
        };

        // Act
        var importer = new SimpleNoteImporter(
            _fs,
            config,
            _notesDir,
            Path.Combine(_sourceDir, "notes.json"),
            _outputDir
        );

        var result = importer.Import();

        // Assert
        result.SuccessfulNotes.ShouldBe(2);

        // Verify folders were created
        var cocktailsDir = Path.Combine(_outputDir, "cocktails");
        Directory.Exists(cocktailsDir).ShouldBeTrue();

        var recipesDir = Path.Combine(_outputDir, "recipes");
        Directory.Exists(recipesDir).ShouldBeTrue();

        // Verify files in correct folders
        File.Exists(Path.Combine(cocktailsDir, "Cocktail Recipe.md")).ShouldBeTrue();
        File.Exists(Path.Combine(recipesDir, "Food Recipe.md")).ShouldBeTrue();
    }

    private void CreateTestData()
    {
        // Create notes.json
        var json = @"{
            ""activeNotes"": [
                {
                    ""id"": ""note1"",
                    ""content"": ""Test Note 1\nContent for note 1"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [""tag1""],
                    ""systemTags"": [],
                    ""pinned"": false
                },
                {
                    ""id"": ""note2"",
                    ""content"": ""Test Note 2\nContent for note 2"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [""tag2""],
                    ""systemTags"": [""markdown""],
                    ""pinned"": true
                }
            ],
            ""trashedNotes"": []
        }";

        File.WriteAllText(Path.Combine(_sourceDir, "notes.json"), json);

        // Create .txt files
        File.WriteAllText(Path.Combine(_notesDir, "Test Note 1.txt"), "Test Note 1\nContent for note 1");
        File.WriteAllText(Path.Combine(_notesDir, "Test Note 2.txt"), "Test Note 2\nContent for note 2");
    }

    private void CreateTestDataWithMessyFormatting()
    {
        var json = @"{
            ""activeNotes"": [
                {
                    ""id"": ""note1"",
                    ""content"": ""Messy Note\nContent"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [],
                    ""systemTags"": [],
                    ""pinned"": false
                }
            ],
            ""trashedNotes"": []
        }";

        File.WriteAllText(Path.Combine(_sourceDir, "notes.json"), json);

        // Create note with messy formatting
        var messyContent = @"Messy Note
#Header


-Item 1
-Item 2";

        File.WriteAllText(Path.Combine(_notesDir, "Messy Note.txt"), messyContent);
    }

    private void CreateTestDataWithTags()
    {
        var json = @"{
            ""activeNotes"": [
                {
                    ""id"": ""note1"",
                    ""content"": ""Cocktail Recipe\nMix ingredients"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [""cocktails""],
                    ""systemTags"": [],
                    ""pinned"": false
                },
                {
                    ""id"": ""note2"",
                    ""content"": ""Food Recipe\nCook ingredients"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [""recipes""],
                    ""systemTags"": [],
                    ""pinned"": false
                }
            ],
            ""trashedNotes"": []
        }";

        File.WriteAllText(Path.Combine(_sourceDir, "notes.json"), json);

        File.WriteAllText(Path.Combine(_notesDir, "Cocktail Recipe.txt"), "Cocktail Recipe\nMix ingredients");
        File.WriteAllText(Path.Combine(_notesDir, "Food Recipe.txt"), "Food Recipe\nCook ingredients");
    }

    private void CleanTestDirectory()
    {
        // Clean notes directory
        if (Directory.Exists(_notesDir))
        {
            foreach (var file in Directory.GetFiles(_notesDir, "*.txt"))
            {
                File.Delete(file);
            }
        }

        // Clean source directory
        if (Directory.Exists(_sourceDir))
        {
            foreach (var file in Directory.GetFiles(_sourceDir))
            {
                File.Delete(file);
            }
        }

        // Clean output directory
        if (Directory.Exists(_outputDir))
        {
            Directory.Delete(_outputDir, recursive: true);
        }
    }

    public void Dispose()
    {
        if (Directory.Exists(_testDir))
        {
            Directory.Delete(_testDir, recursive: true);
        }
    }
}
