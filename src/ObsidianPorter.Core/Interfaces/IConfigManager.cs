namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Manages loading and saving of configuration files.
/// </summary>
public interface IConfigManager
{
    ImportConfig LoadFromFile(string configPath);
    void SaveToFile(string configPath, ImportConfig config);

    // Current configuration state
    void SetCurrentConfig(ImportConfig config, string notesDirectory, string jsonPath, string outputDirectory);
    ImportConfig GetConfig();
    string GetNotesDirectory();
    string GetJsonPath();
    string GetOutputDirectory();
}
