namespace ObsidianPorter.Core.Services;

using Microsoft.Extensions.DependencyInjection;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Factory for creating SimpleNoteImporter instances with runtime parameters.
/// </summary>
public class SimpleNoteImporterFactory(
    IServiceProvider serviceProvider,
    IConfigManager configManager) : ISimpleNoteImporterFactory
{
    private readonly IServiceProvider _serviceProvider = serviceProvider;
    private readonly IConfigManager _configManager = configManager;

    public ISimpleNoteImporter Create(
        ImportConfig config,
        string notesDirectory,
        string jsonPath,
        string outputDirectory)
    {
        // Set configuration state
        _configManager.SetCurrentConfig(config, notesDirectory, jsonPath, outputDirectory);

        // Resolve importer from DI (all dependencies injected automatically)
        return _serviceProvider.GetRequiredService<ISimpleNoteImporter>();
    }
}
