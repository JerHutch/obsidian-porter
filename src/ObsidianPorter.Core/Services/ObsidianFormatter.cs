namespace ObsidianPorter.Core.Services;

using System.Text;
using System.Text.RegularExpressions;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Formats notes as Obsidian-compatible markdown with YAML frontmatter.
/// </summary>
public partial class ObsidianFormatter(IFileSystemService fileSystem, IConfigManager configManager) : IObsidianFormatter
{
    private readonly IFileSystemService _fileSystem = fileSystem;
    private readonly string _outputDirectory = configManager.GetOutputDirectory();

    /// <summary>
    /// Formats a note with YAML frontmatter and saves it to the output directory.
    /// </summary>
    public void FormatAndSave(string content, NoteMetadata metadata, Dictionary<string, object> context)
    {
        // Generate YAML frontmatter
        var frontmatter = GenerateYamlFrontmatter(metadata);

        // Combine frontmatter and content
        var fullContent = $"{frontmatter}\n{content}";

        // Determine output path
        var folder = context.TryGetValue("folder", out var f) ? f?.ToString() : null;
        var filename = SanitizeFilename(metadata.Title);
        var outputPath = BuildOutputPath(folder, filename);

        // Ensure directory exists
        var directory = Path.GetDirectoryName(outputPath);
        if (directory != null && !_fileSystem.DirectoryExists(directory))
        {
            _fileSystem.CreateDirectory(directory);
        }

        // Write file
        _fileSystem.WriteAllText(outputPath, fullContent);
    }

    private static string GenerateYamlFrontmatter(NoteMetadata metadata)
    {
        var sb = new StringBuilder();
        sb.AppendLine("---");
        sb.AppendLine($"title: \"{EscapeYamlString(metadata.Title)}\"");
        sb.AppendLine($"created: \"{metadata.Created:yyyy-MM-ddTHH:mm:sszzz}\"");
        sb.AppendLine($"modified: \"{metadata.Modified:yyyy-MM-ddTHH:mm:sszzz}\"");
        sb.AppendLine("source: \"simplenote\"");
        sb.AppendLine($"original_id: \"{metadata.OriginalId}\"");

        // Tags
        if (metadata.Tags.Any())
        {
            sb.AppendLine("tags:");
            foreach (var tag in metadata.Tags)
            {
                sb.AppendLine($"  - {tag}");
            }
        }
        else
        {
            sb.AppendLine("tags: []");
        }

        sb.AppendLine($"markdown: {metadata.IsMarkdown.ToString().ToLowerInvariant()}");
        sb.AppendLine($"pinned: {metadata.IsPinned.ToString().ToLowerInvariant()}");

        // Category (if present)
        if (!string.IsNullOrWhiteSpace(metadata.Category))
        {
            sb.AppendLine($"category: \"{metadata.Category}\"");
        }

        sb.AppendLine("---");

        return sb.ToString();
    }

    private static string EscapeYamlString(string value)
    {
        // Escape quotes in YAML strings
        return value.Replace("\"", "\\\"");
    }

    private string SanitizeFilename(string title)
    {
        // Remove invalid filename characters
        var sanitized = InvalidFileNameCharsRegex().Replace(title, "");

        // Collapse 3+ consecutive spaces into 2 spaces
        sanitized = MultipleSpacesRegex().Replace(sanitized, "  ");
        sanitized = sanitized.Trim();

        if (string.IsNullOrWhiteSpace(sanitized))
        {
            sanitized = "Untitled";
        }

        return sanitized + ".md";
    }

    private string BuildOutputPath(string? folder, string filename)
    {
        if (string.IsNullOrWhiteSpace(folder))
        {
            return Path.Combine(_outputDirectory, filename);
        }

        return Path.Combine(_outputDirectory, folder, filename);
    }

    [GeneratedRegex(@"[<>:""/\\|?*]")]
    private static partial Regex InvalidFileNameCharsRegex();

    [GeneratedRegex(@"\s{3,}")]
    private static partial Regex MultipleSpacesRegex();
}
