namespace ObsidianPorter.Core;

using Microsoft.Extensions.DependencyInjection;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

/// <summary>
/// Extension methods for registering ObsidianPorter services with dependency injection.
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Adds all ObsidianPorter services to the service collection.
    /// </summary>
    /// <param name="services">The service collection to add services to.</param>
    /// <returns>The service collection for chaining.</returns>
    public static IServiceCollection AddObsidianPorterServices(this IServiceCollection services)
    {
        // Singleton - ConfigManager holds state for current import operation
        services.AddSingleton<IConfigManager, ConfigManager>();

        // Scoped - New instances per import operation (per scope)
        services.AddScoped<IFileSystemService, FileSystemService>();
        services.AddScoped<IMetadataParser, MetadataParser>();
        services.AddScoped<IContentProcessorService, ContentProcessor>();
        services.AddScoped<IObsidianFormatter, ObsidianFormatter>();
        services.AddScoped<ISimpleNoteImporter, SimpleNoteImporter>();
        services.AddScoped<ISimpleNoteImporterFactory, SimpleNoteImporterFactory>();

        return services;
    }
}
