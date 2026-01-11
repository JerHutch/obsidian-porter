namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Services;

public class EditorPipelineTests
{
    private class TestProcessor1 : IPipelineProcessor
    {
        public string Name => "processor1";

        public (string Content, NoteMetadata Metadata) Process(
            string content,
            NoteMetadata metadata,
            Dictionary<string, object> context)
        {
            context["processor1_ran"] = true;
            return (content + " [P1]", metadata with { Tags = metadata.Tags.Append("p1").ToList() });
        }

        public bool ShouldProcess(NoteMetadata metadata, Dictionary<string, object> context) => true;
    }

    private class TestProcessor2 : IPipelineProcessor
    {
        public string Name => "processor2";

        public (string Content, NoteMetadata Metadata) Process(
            string content,
            NoteMetadata metadata,
            Dictionary<string, object> context)
        {
            context["processor2_ran"] = true;
            return (content + " [P2]", metadata with { Tags = metadata.Tags.Append("p2").ToList() });
        }

        public bool ShouldProcess(NoteMetadata metadata, Dictionary<string, object> context) => true;
    }

    [Test]
    public void ProcessNote_WithMultipleProcessors_RunsThemInSequence()
    {
        var processors = new List<IPipelineProcessor> { new TestProcessor1(), new TestProcessor2() };
        var pipeline = new EditorPipeline(processors);
        var metadata = CreateBasicMetadata();

        var (content, updatedMetadata, context) = pipeline.ProcessNote("Original", metadata, "test.txt");

        content.ShouldBe("Original [P1] [P2]");
        updatedMetadata.Tags.ShouldContain("p1");
        updatedMetadata.Tags.ShouldContain("p2");
        context["processor1_ran"].ShouldBe(true);
        context["processor2_ran"].ShouldBe(true);
    }

    [Test]
    public void ProcessNote_WithNoProcessors_ReturnsUnchangedNote()
    {
        var pipeline = new EditorPipeline(new List<IPipelineProcessor>());
        var metadata = CreateBasicMetadata();

        var (content, updatedMetadata, context) = pipeline.ProcessNote("Content", metadata, "test.txt");

        content.ShouldBe("Content");
        updatedMetadata.ShouldBe(metadata);
    }

    [Test]
    public void ProcessNote_WithConditionalProcessor_OnlyRunsWhenShouldProcess()
    {
        var conditionalProcessor = Substitute.For<IPipelineProcessor>();
        conditionalProcessor.Name.Returns("conditional");
        conditionalProcessor.ShouldProcess(Arg.Any<NoteMetadata>(), Arg.Any<Dictionary<string, object>>())
            .Returns(false);

        var pipeline = new EditorPipeline(new List<IPipelineProcessor> { conditionalProcessor });
        var metadata = CreateBasicMetadata();

        var (content, updatedMetadata, context) = pipeline.ProcessNote("Content", metadata, "test.txt");

        conditionalProcessor.DidNotReceive().Process(
            Arg.Any<string>(),
            Arg.Any<NoteMetadata>(),
            Arg.Any<Dictionary<string, object>>()
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
