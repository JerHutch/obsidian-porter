namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Interface for content processing pipeline components.
/// </summary>
public interface IContentProcessor
{
    string Name { get; }

    (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context);

    bool ShouldProcess(NoteMetadata metadata, Dictionary<string, object> context);
}
