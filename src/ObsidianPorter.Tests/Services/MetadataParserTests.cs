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
