namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

/// <summary>
/// Manages loading and saving of configuration files.
/// </summary>
public class ConfigManager(IFileSystemService fileSystem)
{
    private readonly IFileSystemService _fileSystem = fileSystem;

    public ImportConfig LoadFromFile(string configPath)
    {
        if (!_fileSystem.FileExists(configPath))
        {
            return new ImportConfig();
        }

        try
        {
            var yaml = _fileSystem.ReadAllText(configPath);
            var deserializer = new DeserializerBuilder()
                .WithNamingConvention(PascalCaseNamingConvention.Instance)
                .Build();

            return deserializer.Deserialize<ImportConfig>(yaml) ?? new ImportConfig();
        }
        catch
        {
            return new ImportConfig();
        }
    }

    public void SaveToFile(string configPath, ImportConfig config)
    {
        var serializer = new SerializerBuilder()
            .WithNamingConvention(PascalCaseNamingConvention.Instance)
            .Build();

        var yaml = serializer.Serialize(config);
        _fileSystem.WriteAllText(configPath, yaml);
    }
}
