namespace ObsidianPorter.Core.Models;

/// <summary>
/// Represents metadata for a SimpleNote note.
/// </summary>
/// <param name="Title">The note title (from first line).</param>
/// <param name="Created">Creation timestamp.</param>
/// <param name="Modified">Last modified timestamp.</param>
/// <param name="OriginalId">SimpleNote's original note ID.</param>
/// <param name="Tags">Collection of tags.</param>
/// <param name="IsMarkdown">Whether the note uses markdown formatting.</param>
/// <param name="IsPinned">Whether the note is pinned.</param>
/// <param name="Category">Optional category assigned to the note.</param>
public record NoteMetadata(
    string Title,
    DateTime Created,
    DateTime Modified,
    string OriginalId,
    IReadOnlyList<string> Tags,
    bool IsMarkdown,
    bool IsPinned,
    string? Category
);
