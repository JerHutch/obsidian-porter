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
