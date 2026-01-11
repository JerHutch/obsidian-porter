namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Pipelines;

/// <summary>
/// Main orchestrator for importing SimpleNote exports to Obsidian.
/// </summary>
public class SimpleNoteImporter(
    IFileSystemService fileSystem,
    IConfigManager configManager,
    IMetadataParser metadataParser,
    IContentProcessorService contentProcessor,
    IObsidianFormatter formatter) : ISimpleNoteImporter
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private readonly IConfigManager _configManager = configManager;
    private readonly IMetadataParser _metadataParser = metadataParser;
    private readonly IContentProcessorService _contentProcessor = contentProcessor;
    private readonly IObsidianFormatter _formatter = formatter;

    /// <summary>
    /// Executes the import process.
    /// </summary>
    /// <returns>Import statistics.</returns>
    public ImportResult Import()
    {
        var totalNotes = 0;
        var successfulNotes = 0;
        var failedNotes = 0;

        // Get configuration
        var config = _configManager.GetConfig();

        // Step 1: Parse metadata from JSON
        var metadataMap = _metadataParser.Parse();

        // Step 2: Process all .txt files
        var processedNotes = _contentProcessor.ProcessAllNotes();

        // Step 3: Merge metadata with content
        var notes = MergeMetadataWithContent(processedNotes, metadataMap);

        // Step 4: Setup editor pipeline (if enabled)
        EditorPipeline? editorPipeline = null;
        if (config.EnableEditorPipeline)
        {
            var processors = BuildProcessors(config);
            editorPipeline = new EditorPipeline(processors);
        }

        // Step 5: Format and save each note using injected formatter

        foreach (var note in notes)
        {
            totalNotes++;

            try
            {
                var content = note.Content;
                var metadata = note.Metadata;
                var context = new Dictionary<string, object>();

                // Run through editor pipeline if enabled
                if (editorPipeline != null)
                {
                    (content, metadata, context) = editorPipeline.ProcessNote(
                        content,
                        metadata,
                        note.Filename
                    );
                }

                // Format and save
                _formatter.FormatAndSave(content, metadata, context);

                successfulNotes++;
            }
            catch
            {
                failedNotes++;
            }
        }

        return new ImportResult(totalNotes, successfulNotes, failedNotes);
    }

    private List<ProcessedNote> MergeMetadataWithContent(
        List<ProcessedNote> processedNotes,
        Dictionary<string, NoteMetadata> metadataMap)
    {
        var result = new List<ProcessedNote>();

        foreach (var note in processedNotes)
        {
            // Try to find matching metadata
            if (metadataMap.TryGetValue(note.Filename, out var metadata))
            {
                // Use metadata from JSON
                result.Add(note with { Metadata = metadata });
            }
            else
            {
                // Use default metadata from content processor
                result.Add(note);
            }
        }

        return result;
    }

    private List<IPipelineProcessor> BuildProcessors(ImportConfig config)
    {
        var processors = new List<IPipelineProcessor>();

        // Tag Injector
        if (config.EnableAutoTagging)
        {
            processors.Add(new TagInjector(
                config.CustomTagRules,
                config.PropagateCategoryTag
            ));
        }

        // Content Transformer
        if (config.EnableContentTransformation)
        {
            processors.Add(new ContentTransformer(
                config.CleanWhitespace,
                config.StandardizeHeaders,
                config.FixListFormatting
            ));
        }

        // Folder Organizer
        if (config.EnableFolderOrganization)
        {
            processors.Add(new FolderOrganizer(config.CustomFolderRules));
        }

        return processors;
    }
}
