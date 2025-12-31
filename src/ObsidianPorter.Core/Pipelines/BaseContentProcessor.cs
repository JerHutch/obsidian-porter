namespace ObsidianPorter.Core.Pipelines;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Base class for content processors in the editor pipeline.
/// </summary>
public abstract class BaseContentProcessor : IContentProcessor
{
    public abstract string Name { get; }

    public abstract (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context);

    public virtual bool ShouldProcess(NoteMetadata metadata, Dictionary<string, object> context)
    {
        return true; // Process by default
    }
}
