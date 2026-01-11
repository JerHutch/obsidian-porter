namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Orchestrates the execution of content processors in the editor pipeline.
/// </summary>
public class EditorPipeline(IEnumerable<IPipelineProcessor> processors)
{
    private readonly List<IPipelineProcessor> _processors = processors.ToList();

    /// <summary>
    /// Processes a note through all registered processors.
    /// </summary>
    /// <param name="content">The note content.</param>
    /// <param name="metadata">The note metadata.</param>
    /// <param name="filename">The source filename.</param>
    /// <returns>A tuple containing the processed content, updated metadata, and context.</returns>
    public (string Content, NoteMetadata Metadata, Dictionary<string, object> Context) ProcessNote(
        string content,
        NoteMetadata metadata,
        string filename)
    {
        var currentContent = content;
        var currentMetadata = metadata;
        var context = new Dictionary<string, object>
        {
            { "filename", filename }
        };

        foreach (var processor in _processors)
        {
            // Check if processor should run
            if (!processor.ShouldProcess(currentMetadata, context))
            {
                continue;
            }

            // Run processor
            (currentContent, currentMetadata) = processor.Process(currentContent, currentMetadata, context);
        }

        return (currentContent, currentMetadata, context);
    }
}
