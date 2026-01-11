namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Services;

public class ObsidianFormatterTests
{
    [Test]
    public void FormatAndSave_GeneratesYamlFrontmatter()
    {
        var fs = Substitute.For<IFileSystemService>();
        var configManager = Substitute.For<IConfigManager>();
        configManager.GetOutputDirectory().Returns("/output");

        var formatter = new ObsidianFormatter(fs, configManager);
        var metadata = new NoteMetadata(
            Title: "Test Note",
            Created: new DateTime(2024, 1, 1, 12, 0, 0, DateTimeKind.Utc),
            Modified: new DateTime(2024, 1, 2, 14, 30, 0, DateTimeKind.Utc),
            OriginalId: "abc123",
            Tags: new List<string> { "tag1", "tag2" },
            IsMarkdown: true,
            IsPinned: false,
            Category: "recipes"
        );
        var context = new Dictionary<string, object> { { "folder", "recipes" } };

        formatter.FormatAndSave("Content here", metadata, context);

        fs.Received(1).WriteAllText(
            Arg.Is<string>(path => path.Contains("recipes") && path.EndsWith(".md")),
            Arg.Is<string>(content =>
                content.Contains("---") &&
                content.Contains("title: \"Test Note\"") &&
                content.Contains("created: \"2024-01-01T12:00:00+00:00\"") &&
                content.Contains("modified: \"2024-01-02T14:30:00+00:00\"") &&
                content.Contains("source: \"simplenote\"") &&
                content.Contains("original_id: \"abc123\"") &&
                content.Contains("- tag1") &&
                content.Contains("- tag2") &&
                content.Contains("markdown: true") &&
                content.Contains("pinned: false") &&
                content.Contains("category: \"recipes\"") &&
                content.Contains("Content here")
            )
        );
    }

    [Test]
    public void FormatAndSave_SanitizesFilename()
    {
        var fs = Substitute.For<IFileSystemService>();
        var configManager = Substitute.For<IConfigManager>();
        configManager.GetOutputDirectory().Returns("/output");

        var formatter = new ObsidianFormatter(fs, configManager);
        var metadata = new NoteMetadata(
            Title: "Test: Note / With \\ Bad * Chars?",
            Created: DateTime.UtcNow,
            Modified: DateTime.UtcNow,
            OriginalId: "123",
            Tags: [],
            IsMarkdown: false,
            IsPinned: false,
            Category: null
        );
        var context = new Dictionary<string, object> { { "folder", "other" } };

        formatter.FormatAndSave("Content", metadata, context);

        fs.Received(1).WriteAllText(
            Arg.Is<string>(path =>
                path.Contains("Test Note  With  Bad  Chars") &&
                !path.Contains(":") &&
                !path.Contains("?") &&
                !path.Contains("*")
            ),
            Arg.Any<string>()
        );
    }

    [Test]
    public void FormatAndSave_CreatesDirectoryIfNotExists()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.DirectoryExists(Arg.Any<string>()).Returns(false);
        var configManager = Substitute.For<IConfigManager>();
        configManager.GetOutputDirectory().Returns("/output");

        var formatter = new ObsidianFormatter(fs, configManager);
        var metadata = CreateBasicMetadata();
        var context = new Dictionary<string, object> { { "folder", "cocktails" } };

        formatter.FormatAndSave("Content", metadata, context);

        fs.Received(1).CreateDirectory(Arg.Is<string>(path => path.Contains("cocktails")));
    }

    [Test]
    public void FormatAndSave_WithNoFolder_UsesRootDirectory()
    {
        var fs = Substitute.For<IFileSystemService>();
        var configManager = Substitute.For<IConfigManager>();
        configManager.GetOutputDirectory().Returns("/output");

        var formatter = new ObsidianFormatter(fs, configManager);
        var metadata = CreateBasicMetadata();
        var context = new Dictionary<string, object>();

        formatter.FormatAndSave("Content", metadata, context);

        fs.Received(1).WriteAllText(
            Arg.Is<string>(path => path == "/output/Test.md"),
            Arg.Any<string>()
        );
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
