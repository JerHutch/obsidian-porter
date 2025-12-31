namespace ObsidianPorter.Tests.Models;

using Shouldly;
using ObsidianPorter.Core.Models;

public class ImportConfigTests
{
    [Test]
    public void DefaultConfig_HasPhase2FeaturesEnabled()
    {
        var config = new ImportConfig();

        config.EnableEditorPipeline.ShouldBeTrue();
        config.EnableAutoTagging.ShouldBeTrue();
        config.EnableFolderOrganization.ShouldBeTrue();
        config.EnableContentTransformation.ShouldBeTrue();
    }

    [Test]
    public void DefaultConfig_HasPhase3FeaturesDisabled()
    {
        var config = new ImportConfig();

        config.EnableNoteSplitting.ShouldBeFalse();
        config.EnableLlmCategorization.ShouldBeFalse();
    }

    [Test]
    public void Categories_DefaultConfig_ContainsExpectedCategories()
    {
        var config = new ImportConfig();

        config.Categories.ShouldContain(c => c.Slug == "cocktails");
        config.Categories.ShouldContain(c => c.Slug == "recipes");
        config.Categories.ShouldContain(c => c.Slug == "other");
    }
}
