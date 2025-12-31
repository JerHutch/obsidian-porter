namespace ObsidianPorter.Core.Pipelines;

using System.Text.RegularExpressions;
using ObsidianPorter.Core.Models;

/// <summary>
/// Adds tags based on content analysis and filename patterns.
/// </summary>
public partial class TagInjector(
    Dictionary<string, List<string>> tagRules,
    bool propagateCategoryTag) : BaseContentProcessor
{
    private readonly Dictionary<string, List<string>> _tagRules = tagRules;
    private readonly bool _propagateCategoryTag = propagateCategoryTag;

    public override string Name => "tag_injector";

    public override (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context)
    {
        var newTags = new HashSet<string>(metadata.Tags);

        // Extract tags from filename
        var filename = context.TryGetValue("filename", out var fn) ? fn?.ToString() ?? "" : "";
        newTags.UnionWith(ExtractFilenameTagsInternal(filename));

        // Extract tags from content
        newTags.UnionWith(ExtractContentTags(content));

        // Propagate category tag if configured
        if (_propagateCategoryTag && metadata.Category is not null)
        {
            newTags.Add(metadata.Category);
        }

        var updatedMetadata = metadata with { Tags = newTags.OrderBy(t => t).ToList() };
        return (content, updatedMetadata);
    }

    private List<string> ExtractFilenameTagsInternal(string filename)
    {
        var tags = new List<string>();

        // Check for date patterns (journal entries)
        if (DatePatternRegex().IsMatch(filename))
        {
            tags.Add("journal");
        }

        // Check for specific prefixes
        if (filename.StartsWith('#'))
        {
            tags.Add("reference");
        }

        // Apply custom rules
        var filenameLower = filename.ToLowerInvariant();
        foreach (var (pattern, patternTags) in _tagRules)
        {
            if (Regex.IsMatch(filenameLower, pattern, RegexOptions.IgnoreCase))
            {
                tags.AddRange(patternTags);
            }
        }

        return tags;
    }

    private List<string> ExtractContentTags(string content)
    {
        var tags = new List<string>();
        var contentLower = content.ToLowerInvariant();

        // Apply custom rules
        foreach (var (pattern, patternTags) in _tagRules)
        {
            if (Regex.IsMatch(contentLower, pattern, RegexOptions.IgnoreCase))
            {
                tags.AddRange(patternTags);
            }
        }

        // Check for list patterns
        var lines = content.Split('\n');
        var listLines = lines.Count(line =>
            line.TrimStart().StartsWith("- ") ||
            line.TrimStart().StartsWith("* ") ||
            line.TrimStart().StartsWith("+ ") ||
            Regex.IsMatch(line, @"^\s*\d+\.\s"));

        if (listLines > 3)
        {
            tags.Add("lists");
        }

        return tags;
    }

    [GeneratedRegex(@"\d{2}-\d{2}-\d{4}")]
    private static partial Regex DatePatternRegex();
}
