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
