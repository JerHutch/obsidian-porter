namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

public class ConfigManagerTests
{
    [Test]
    public void LoadFromFile_WhenFileDoesNotExist_ReturnsDefaultConfig()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists(Arg.Any<string>()).Returns(false);

        var manager = new ConfigManager(fs);
        var config = manager.LoadFromFile("nonexistent.yaml");

        config.ShouldNotBeNull();
        config.EnableEditorPipeline.ShouldBeTrue();
    }

    [Test]
    public void LoadFromFile_WithValidYaml_LoadsConfiguration()
    {
        var yaml = @"
EnableEditorPipeline: false
EnableAutoTagging: true
CleanWhitespace: false
";
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists("test.yaml").Returns(true);
        fs.ReadAllText("test.yaml").Returns(yaml);

        var manager = new ConfigManager(fs);
        var config = manager.LoadFromFile("test.yaml");

        config.EnableEditorPipeline.ShouldBeFalse();
        config.EnableAutoTagging.ShouldBeTrue();
        config.CleanWhitespace.ShouldBeFalse();
    }
}
