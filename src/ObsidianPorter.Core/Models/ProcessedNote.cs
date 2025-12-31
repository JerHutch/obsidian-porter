namespace ObsidianPorter.Core.Models;

/// <summary>
/// Represents a note after content processing.
/// </summary>
/// <param name="Content">The note's text content.</param>
/// <param name="Metadata">The note's metadata.</param>
/// <param name="Filename">The source filename.</param>
public record ProcessedNote(
    string Content,
    NoteMetadata Metadata,
    string Filename
);
