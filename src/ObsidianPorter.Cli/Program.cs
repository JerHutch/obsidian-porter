using System.CommandLine;
using Microsoft.Extensions.DependencyInjection;
using ObsidianPorter.Core;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

// Build DI container at startup
var services = new ServiceCollection();
services.AddObsidianPorterServices();
var serviceProvider = services.BuildServiceProvider();

var rootCommand = new RootCommand("SimpleNote to Obsidian Importer - Convert SimpleNote exports to Obsidian-compatible markdown");

// Define options
var notesOption = new Option<string>(
    name: "--notes",
    description: "Path to the directory containing SimpleNote .txt files",
    getDefaultValue: () => "data"
);
notesOption.AddAlias("-n");

var jsonOption = new Option<string>(
    name: "--json",
    description: "Path to the notes.json metadata file",
    getDefaultValue: () => "data/source/notes.json"
);
jsonOption.AddAlias("-j");

var outputOption = new Option<string>(
    name: "--output",
    description: "Path to the output directory for Obsidian vault",
    getDefaultValue: () => "output/obsidian_vault"
);
outputOption.AddAlias("-o");

var configOption = new Option<string?>(
    name: "--config",
    description: "Path to configuration YAML file (optional)"
);
configOption.AddAlias("-c");

var smartOption = new Option<bool>(
    name: "--smart",
    description: "Enable smart processing (auto-tagging, folder organization, content transformation)",
    getDefaultValue: () => false
);

rootCommand.AddOption(notesOption);
rootCommand.AddOption(jsonOption);
rootCommand.AddOption(outputOption);
rootCommand.AddOption(configOption);
rootCommand.AddOption(smartOption);

rootCommand.SetHandler((string notesDir, string jsonPath, string outputDir, string? configPath, bool smart) =>
{
    try
    {
        Console.WriteLine("SimpleNote to Obsidian Importer");
        Console.WriteLine("================================\n");

        // Create scope for this import operation
        using var scope = serviceProvider.CreateScope();
        var scopedServices = scope.ServiceProvider;

        // Resolve services from DI
        var configManager = scopedServices.GetRequiredService<IConfigManager>();
        var importerFactory = scopedServices.GetRequiredService<ISimpleNoteImporterFactory>();

        // Load configuration
        var config = LoadConfiguration(configManager, configPath, smart);

        Console.WriteLine($"Notes directory: {notesDir}");
        Console.WriteLine($"JSON metadata: {jsonPath}");
        Console.WriteLine($"Output directory: {outputDir}");
        Console.WriteLine($"Smart processing: {(config.EnableEditorPipeline ? "enabled" : "disabled")}\n");

        // Create importer via factory
        var importer = importerFactory.Create(config, notesDir, jsonPath, outputDir);

        Console.WriteLine("Starting import...\n");
        var result = importer.Import();

        // Display results
        Console.WriteLine("\nImport Complete!");
        Console.WriteLine("================");
        Console.WriteLine($"Total notes processed: {result.TotalNotes}");
        Console.WriteLine($"Successfully imported: {result.SuccessfulNotes}");
        Console.WriteLine($"Failed: {result.FailedNotes}");

        if (result.FailedNotes > 0)
        {
            Console.WriteLine("\nWarning: Some notes failed to import. Check the error messages above for details.");
        }

        Console.WriteLine($"\nOutput written to: {Path.GetFullPath(outputDir)}");
    }
    catch (Exception ex)
    {
        Console.Error.WriteLine($"\nError: {ex.Message}");
        Console.Error.WriteLine($"\nStack trace:\n{ex.StackTrace}");
        Environment.Exit(1);
    }
}, notesOption, jsonOption, outputOption, configOption, smartOption);

return await rootCommand.InvokeAsync(args);

static ImportConfig LoadConfiguration(IConfigManager configManager, string? configPath, bool smart)
{
    ImportConfig config;

    if (!string.IsNullOrWhiteSpace(configPath))
    {
        // Load from file
        config = configManager.LoadFromFile(configPath);
        Console.WriteLine($"Configuration loaded from: {configPath}");
    }
    else if (smart)
    {
        // Use default smart configuration
        config = new ImportConfig
        {
            EnableEditorPipeline = true,
            EnableAutoTagging = true,
            EnableFolderOrganization = true,
            EnableContentTransformation = true
        };
        Console.WriteLine("Using default smart configuration");
    }
    else
    {
        // Use minimal configuration
        config = new ImportConfig
        {
            EnableEditorPipeline = false
        };
        Console.WriteLine("Using minimal configuration (Phase 1 compatibility)");
    }

    return config;
}
