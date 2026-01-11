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
