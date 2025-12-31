namespace ObsidianPorter.Tests.Pipelines;

using Shouldly;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Pipelines;

public class FolderOrganizerTests
{
    [Test]
    public void Process_WithCocktailsTag_AssignsCocktailsFolder()
    {
        var organizer = new FolderOrganizer(new Dictionary<string, string>());
        var metadata = CreateBasicMetadata() with
        {
            Tags = new List<string> { "cocktails", "drinks" }
        };
        var context = new Dictionary<string, object> { { "filename", "old-fashioned.txt" } };

        var (_, updatedMetadata) = organizer.Process("content", metadata, context);
        var folder = context["folder"] as string;

        folder.ShouldBe("cocktails");
    }

    [Test]
    public void Process_WithCategorySet_PrefersCategoryOverTags()
    {
        var organizer = new FolderOrganizer(new Dictionary<string, string>());
        var metadata = CreateBasicMetadata() with
        {
            Category = "recipes",
            Tags = new List<string> { "cocktails", "drinks" }
        };
        var context = new Dictionary<string, object> { { "filename", "recipe.txt" } };

        var (_, updatedMetadata) = organizer.Process("content", metadata, context);
        var folder = context["folder"] as string;

        folder.ShouldBe("recipes");
    }

    [Test]
    public void Process_WithCustomRules_AppliesCustomFolderMapping()
    {
        var customRules = new Dictionary<string, string>
        {
            { "gaming", "games" },
            { "music", "audio/music" }
        };
        var organizer = new FolderOrganizer(customRules);
        var metadata = CreateBasicMetadata() with
        {
            Tags = new List<string> { "gaming" }
        };
        var context = new Dictionary<string, object> { { "filename", "walkthrough.txt" } };

        var (_, updatedMetadata) = organizer.Process("content", metadata, context);
        var folder = context["folder"] as string;

        folder.ShouldBe("games");
    }

    [Test]
    public void Process_WithNoMatchingTags_AssignsOtherFolder()
    {
        var organizer = new FolderOrganizer(new Dictionary<string, string>());
        var metadata = CreateBasicMetadata() with
        {
            Tags = new List<string> { "random-tag" }
        };
        var context = new Dictionary<string, object> { { "filename", "note.txt" } };

        var (_, updatedMetadata) = organizer.Process("content", metadata, context);
        var folder = context["folder"] as string;

        folder.ShouldBe("other");
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
