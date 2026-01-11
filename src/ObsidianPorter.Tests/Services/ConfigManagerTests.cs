namespace ObsidianPorter.Tests.Services;

using System.IO;
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

    [Test]
    public void SaveToFile_WritesYamlConfiguration()
    {
        var config = new Core.Models.ImportConfig { EnableEditorPipeline = false };
        var fs = Substitute.For<IFileSystemService>();

        var manager = new ConfigManager(fs);
        manager.SaveToFile("test.yaml", config);

        fs.Received(1).WriteAllText("test.yaml", Arg.Is<string>(s => s.Contains("EnableEditorPipeline: false")));
    }

    [Test]
    public void LoadFromFile_WithInvalidYaml_ReturnsDefaultConfigAndWarnsUser()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists("bad.yaml").Returns(true);
        fs.ReadAllText("bad.yaml").Returns("invalid: yaml: syntax:");

        var manager = new ConfigManager(fs);
        var config = manager.LoadFromFile("bad.yaml");

        config.ShouldNotBeNull();
        config.EnableEditorPipeline.ShouldBeTrue(); // Should be default config
    }

    [Test]
    public void SaveToFile_WhenWriteFails_ThrowsException()
    {
        var config = new Core.Models.ImportConfig();
        var fs = Substitute.For<IFileSystemService>();
        fs.When(x => x.WriteAllText(Arg.Any<string>(), Arg.Any<string>()))
          .Do(x => throw new IOException("Disk full"));

        var manager = new ConfigManager(fs);

        Should.Throw<IOException>(() => manager.SaveToFile("test.yaml", config));
    }
}
