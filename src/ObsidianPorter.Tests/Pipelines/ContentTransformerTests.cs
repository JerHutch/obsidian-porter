namespace ObsidianPorter.Tests.Pipelines;

using Shouldly;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Pipelines;

public class ContentTransformerTests
{
    [Test]
    public void Process_WithExtraWhitespace_CleansWhitespace()
    {
        var transformer = new ContentTransformer(
            cleanWhitespace: true,
            standardizeHeaders: false,
            fixListFormatting: false
        );
        var content = "Line 1  \n\n\n\nLine 2   \nLine 3";
        var metadata = CreateBasicMetadata();

        var (cleaned, _) = transformer.Process(content, metadata, new Dictionary<string, object>());

        cleaned.ShouldNotContain("  \n"); // No trailing spaces
        cleaned.Split("\n\n\n").Length.ShouldBe(1); // No triple blank lines
    }

    [Test]
    public void Process_WithInconsistentHeaders_StandardizesHeaders()
    {
        var transformer = new ContentTransformer(
            cleanWhitespace: false,
            standardizeHeaders: true,
            fixListFormatting: false
        );
        var content = "#Header1\n##  Header 2  \n###Header3";
        var metadata = CreateBasicMetadata();

        var (standardized, _) = transformer.Process(content, metadata, new Dictionary<string, object>());

        standardized.ShouldContain("# Header1");
        standardized.ShouldContain("## Header 2");
        standardized.ShouldContain("### Header3");
    }

    [Test]
    public void Process_WithBadListFormatting_FixesLists()
    {
        var transformer = new ContentTransformer(
            cleanWhitespace: false,
            standardizeHeaders: false,
            fixListFormatting: true
        );
        var content = "-Item 1\n-  Item 2\n-Item 3";
        var metadata = CreateBasicMetadata();

        var (fixedContent, _) = transformer.Process(content, metadata, new Dictionary<string, object>());

        fixedContent.ShouldContain("- Item 1");
        fixedContent.ShouldContain("- Item 2");
        fixedContent.ShouldContain("- Item 3");
    }

    [Test]
    public void Process_WithAllTransformationsEnabled_AppliesAll()
    {
        var transformer = new ContentTransformer(
            cleanWhitespace: true,
            standardizeHeaders: true,
            fixListFormatting: true
        );
        var content = "#Header  \n\n\n\n-Item 1\n-Item 2";
        var metadata = CreateBasicMetadata();

        var (transformed, _) = transformer.Process(content, metadata, new Dictionary<string, object>());

        transformed.ShouldContain("# Header");
        transformed.ShouldNotContain("Header  ");
        transformed.ShouldContain("- Item 1");
        transformed.ShouldContain("- Item 2");
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
