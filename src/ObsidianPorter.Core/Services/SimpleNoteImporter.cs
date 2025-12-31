namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;
using ObsidianPorter.Core.Pipelines;

/// <summary>
/// Main orchestrator for importing SimpleNote exports to Obsidian.
/// </summary>
public class SimpleNoteImporter(
    IFileSystemService fileSystem,
    ImportConfig config,
    string notesDirectory,
    string jsonPath,
    string outputDirectory)
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private readonly ImportConfig _config = config;
    private readonly string _notesDirectory = notesDirectory;
    private readonly string _jsonPath = jsonPath;
    private readonly string _outputDirectory = outputDirectory;

    /// <summary>
    /// Executes the import process.
    /// </summary>
    /// <returns>Import statistics.</returns>
    public ImportResult Import()
    {
        var totalNotes = 0;
        var successfulNotes = 0;
        var failedNotes = 0;

        // Step 1: Parse metadata from JSON
        var metadataParser = new MetadataParser(_fileSystem, _jsonPath);
        var metadataMap = metadataParser.Parse();

        // Step 2: Process all .txt files
        var contentProcessor = new ContentProcessor(_fileSystem, _notesDirectory);
        var processedNotes = contentProcessor.ProcessAllNotes();

        // Step 3: Merge metadata with content
        var notes = MergeMetadataWithContent(processedNotes, metadataMap);

        // Step 4: Setup editor pipeline (if enabled)
        EditorPipeline? editorPipeline = null;
        if (_config.EnableEditorPipeline)
        {
            var processors = BuildProcessors();
            editorPipeline = new EditorPipeline(processors);
        }

        // Step 5: Format and save each note
        var formatter = new ObsidianFormatter(_fileSystem, _outputDirectory);

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
                formatter.FormatAndSave(content, metadata, context);

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

    private List<IContentProcessor> BuildProcessors()
    {
        var processors = new List<IContentProcessor>();

        // Tag Injector
        if (_config.EnableAutoTagging)
        {
            processors.Add(new TagInjector(
                _config.CustomTagRules,
                _config.PropagateCategoryTag
            ));
        }

        // Content Transformer
        if (_config.EnableContentTransformation)
        {
            processors.Add(new ContentTransformer(
                _config.CleanWhitespace,
                _config.StandardizeHeaders,
                _config.FixListFormatting
            ));
        }

        // Folder Organizer
        if (_config.EnableFolderOrganization)
        {
            processors.Add(new FolderOrganizer(_config.CustomFolderRules));
        }

        return processors;
    }
}
