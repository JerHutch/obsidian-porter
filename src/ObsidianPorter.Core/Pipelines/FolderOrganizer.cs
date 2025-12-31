namespace ObsidianPorter.Core.Pipelines;

using ObsidianPorter.Core.Models;

/// <summary>
/// Organizes notes into folders based on categories and tags.
/// </summary>
public class FolderOrganizer(Dictionary<string, string> customFolderRules) : BaseContentProcessor
{
    private readonly Dictionary<string, string> _customFolderRules = customFolderRules;

    // Well-known tag-to-folder mappings
    private static readonly Dictionary<string, string> DefaultFolderMappings = new()
    {
        { "cocktails", "cocktails" },
        { "recipes", "recipes" },
        { "gaming", "gaming" },
        { "music", "music" },
        { "track-lists", "track-lists" },
        { "house", "house" },
        { "role-playing-games", "role-playing-games" },
        { "cisco", "cisco" },
        { "journal", "journal" },
        { "reference", "reference" },
        { "lists", "lists" }
    };

    public override string Name => "folder_organizer";

    public override (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context)
    {
        var folder = DetermineFolder(metadata);

        // Store folder in context for use by formatter
        context["folder"] = folder;

        return (content, metadata);
    }

    private string DetermineFolder(NoteMetadata metadata)
    {
        // 1. Prefer category if set
        if (!string.IsNullOrWhiteSpace(metadata.Category))
        {
            // Check custom rules first
            if (_customFolderRules.TryGetValue(metadata.Category, out var customFolder))
            {
                return customFolder;
            }

            // Use category as-is
            return metadata.Category;
        }

        // 2. Check tags against custom rules
        foreach (var tag in metadata.Tags)
        {
            if (_customFolderRules.TryGetValue(tag, out var customFolder))
            {
                return customFolder;
            }
        }

        // 3. Check tags against default mappings
        foreach (var tag in metadata.Tags)
        {
            if (DefaultFolderMappings.TryGetValue(tag, out var defaultFolder))
            {
                return defaultFolder;
            }
        }

        // 4. Default to "other"
        return "other";
    }
}
