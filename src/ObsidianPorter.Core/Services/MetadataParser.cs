namespace ObsidianPorter.Core.Services;

using System.Text.Json;
using System.Text.RegularExpressions;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Parses metadata from SimpleNote JSON export.
/// </summary>
public partial class MetadataParser(IFileSystemService fileSystem, string jsonPath)
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private readonly string _jsonPath = jsonPath;

    public Dictionary<string, NoteMetadata> Parse()
    {
        if (!_fileSystem.FileExists(_jsonPath))
        {
            return new Dictionary<string, NoteMetadata>();
        }

        try
        {
            var json = _fileSystem.ReadAllText(_jsonPath);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var metadataMap = new Dictionary<string, NoteMetadata>();

            if (root.TryGetProperty("activeNotes", out var activeNotes))
            {
                foreach (var note in activeNotes.EnumerateArray())
                {
                    var metadata = ParseNote(note);
                    var filename = GenerateFilename(metadata.Title);
                    metadataMap[filename] = metadata;
                }
            }

            return metadataMap;
        }
        catch
        {
            return new Dictionary<string, NoteMetadata>();
        }
    }

    private static NoteMetadata ParseNote(JsonElement note)
    {
        var content = note.GetProperty("content").GetString() ?? "";
        var title = ExtractTitle(content);
        var id = note.GetProperty("id").GetString() ?? "";
        var created = DateTime.Parse(note.GetProperty("creationDate").GetString() ?? DateTime.UtcNow.ToString());
        var modified = DateTime.Parse(note.GetProperty("lastModified").GetString() ?? DateTime.UtcNow.ToString());

        var tags = new List<string>();
        if (note.TryGetProperty("tags", out var tagsElement))
        {
            tags = tagsElement.EnumerateArray().Select(t => t.GetString() ?? "").ToList();
        }

        var isMarkdown = false;
        if (note.TryGetProperty("systemTags", out var systemTags))
        {
            isMarkdown = systemTags.EnumerateArray().Any(t => t.GetString() == "markdown");
        }

        var isPinned = note.TryGetProperty("pinned", out var pinnedElement) && pinnedElement.GetBoolean();

        return new NoteMetadata(
            Title: title,
            Created: created,
            Modified: modified,
            OriginalId: id,
            Tags: tags,
            IsMarkdown: isMarkdown,
            IsPinned: isPinned,
            Category: null
        );
    }

    private static string ExtractTitle(string content)
    {
        var lines = content.Split('\n');
        return lines.Length > 0 ? lines[0].Trim() : "Untitled";
    }

    public string GenerateFilename(string title)
    {
        // Remove invalid filename characters (don't replace, just remove)
        var sanitized = InvalidFileNameCharsRegex().Replace(title, "");

        // Collapse 3+ consecutive spaces into 2 spaces (preserve double spaces as separators)
        sanitized = MultipleSpacesRegex().Replace(sanitized, "  ");
        sanitized = sanitized.Trim();

        if (string.IsNullOrWhiteSpace(sanitized))
        {
            sanitized = "Untitled";
        }

        return sanitized + ".txt";
    }

    [GeneratedRegex(@"[<>:""/\\|?*]")]
    private static partial Regex InvalidFileNameCharsRegex();

    [GeneratedRegex(@"\s{3,}")]
    private static partial Regex MultipleSpacesRegex();
}
