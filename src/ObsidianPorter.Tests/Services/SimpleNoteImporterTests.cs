namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Services;

public class SimpleNoteImporterTests
{
    [Test]
    public void Import_WithValidData_ProcessesAllNotes()
    {
        var fs = Substitute.For<IFileSystemService>();
        SetupFileSystem(fs);

        var config = new ImportConfig
        {
            EnableEditorPipeline = false  // Disable pipeline for simple test
        };

        var importer = CreateImporter(fs, config);
        var result = importer.Import();

        result.TotalNotes.ShouldBe(2);
        result.SuccessfulNotes.ShouldBe(2);
        result.FailedNotes.ShouldBe(0);

        // Verify files were written
        fs.Received(2).WriteAllText(
            Arg.Is<string>(path => path.EndsWith(".md")),
            Arg.Any<string>()
        );
    }

    [Test]
    public void Import_WithEditorPipeline_AppliesProcessors()
    {
        var fs = Substitute.For<IFileSystemService>();
        SetupFileSystem(fs);

        var config = new ImportConfig
        {
            EnableEditorPipeline = true,
            EnableAutoTagging = true,
            EnableContentTransformation = true,
            EnableFolderOrganization = true
        };

        var importer = CreateImporter(fs, config);
        var result = importer.Import();

        result.TotalNotes.ShouldBe(2);
        result.SuccessfulNotes.ShouldBe(2);

        // Verify files were processed and written
        fs.Received(2).WriteAllText(
            Arg.Any<string>(),
            Arg.Any<string>()
        );
    }

    [Test]
    public void Import_WhenMetadataNotFound_UsesDefaultMetadata()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.DirectoryExists("/notes").Returns(true);
        fs.GetFiles("/notes", "*.txt").Returns(new[] { "/notes/orphan.txt" });
        fs.ReadAllText("/notes/orphan.txt").Returns("Orphan Note\nNo metadata");
        fs.FileExists("/notes/source/notes.json").Returns(false);  // No JSON file

        var config = new ImportConfig { EnableEditorPipeline = false };

        var importer = CreateImporter(fs, config);
        var result = importer.Import();

        result.TotalNotes.ShouldBe(1);
        result.SuccessfulNotes.ShouldBe(1);

        // Should still create note with default metadata
        fs.Received(1).WriteAllText(
            Arg.Any<string>(),
            Arg.Is<string>(content => content.Contains("source: \"simplenote\""))
        );
    }

    private static SimpleNoteImporter CreateImporter(IFileSystemService fs, ImportConfig config)
    {
        // Setup ConfigManager
        var configManager = Substitute.For<IConfigManager>();
        configManager.GetConfig().Returns(config);
        configManager.GetNotesDirectory().Returns("/notes");
        configManager.GetJsonPath().Returns("/notes/source/notes.json");
        configManager.GetOutputDirectory().Returns("/output");

        // Create real service instances with mocked dependencies
        var metadataParser = new MetadataParser(fs, configManager);
        var contentProcessor = new ContentProcessor(fs, configManager);
        var formatter = new ObsidianFormatter(fs, configManager);

        return new SimpleNoteImporter(fs, configManager, metadataParser, contentProcessor, formatter);
    }

    private static void SetupFileSystem(IFileSystemService fs)
    {
        // Setup directories
        fs.DirectoryExists("/notes").Returns(true);
        fs.DirectoryExists(Arg.Is<string>(p => p.StartsWith("/output"))).Returns(false);

        // Setup JSON metadata
        var json = @"{
            ""activeNotes"": [
                {
                    ""id"": ""note1"",
                    ""content"": ""Note 1\nContent 1"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [""tag1""],
                    ""systemTags"": [],
                    ""pinned"": false
                },
                {
                    ""id"": ""note2"",
                    ""content"": ""Note 2\nContent 2"",
                    ""creationDate"": ""2024-01-01T12:00:00Z"",
                    ""lastModified"": ""2024-01-02T14:30:00Z"",
                    ""tags"": [""tag2""],
                    ""systemTags"": [""markdown""],
                    ""pinned"": true
                }
            ],
            ""trashedNotes"": []
        }";

        fs.FileExists("/notes/source/notes.json").Returns(true);
        fs.ReadAllText("/notes/source/notes.json").Returns(json);

        // Setup .txt files
        fs.GetFiles("/notes", "*.txt").Returns(new[] { "/notes/Note 1.txt", "/notes/Note 2.txt" });
        fs.ReadAllText("/notes/Note 1.txt").Returns("Note 1\nContent 1");
        fs.ReadAllText("/notes/Note 2.txt").Returns("Note 2\nContent 2");
    }
}
