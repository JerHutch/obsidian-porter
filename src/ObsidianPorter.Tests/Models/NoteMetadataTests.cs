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
