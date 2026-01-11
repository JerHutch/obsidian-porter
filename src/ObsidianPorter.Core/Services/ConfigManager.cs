namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

/// <summary>
/// Manages loading and saving of configuration files.
/// </summary>
public class ConfigManager(IFileSystemService fileSystem) : IConfigManager
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private ImportConfig? _currentConfig;
    private string? _notesDirectory;
    private string? _jsonPath;
    private string? _outputDirectory;

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
        catch (Exception ex)
        {
            Console.WriteLine($"Warning: Could not load config from {configPath}: {ex.Message}. Using default configuration.");
            return new ImportConfig();
        }
    }

    public void SaveToFile(string configPath, ImportConfig config)
    {
        try
        {
            var serializer = new SerializerBuilder()
                .WithNamingConvention(PascalCaseNamingConvention.Instance)
                .Build();

            var yaml = serializer.Serialize(config);
            _fileSystem.WriteAllText(configPath, yaml);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Warning: Could not save config to {configPath}: {ex.Message}");
            throw; // Re-throw so caller knows save failed
        }
    }

    public void SetCurrentConfig(
        ImportConfig config,
        string notesDirectory,
        string jsonPath,
        string outputDirectory)
    {
        _currentConfig = config;
        _notesDirectory = notesDirectory;
        _jsonPath = jsonPath;
        _outputDirectory = outputDirectory;
    }

    public ImportConfig GetConfig()
        => _currentConfig ?? throw new InvalidOperationException("Config not set. Call SetCurrentConfig first.");

    public string GetNotesDirectory()
        => _notesDirectory ?? throw new InvalidOperationException("Notes directory not set. Call SetCurrentConfig first.");

    public string GetJsonPath()
        => _jsonPath ?? throw new InvalidOperationException("JSON path not set. Call SetCurrentConfig first.");

    public string GetOutputDirectory()
        => _outputDirectory ?? throw new InvalidOperationException("Output directory not set. Call SetCurrentConfig first.");
}
