namespace ObsidianPorter.Core.Pipelines;

using System.Text.RegularExpressions;
using ObsidianPorter.Core.Models;

/// <summary>
/// Transforms note content with whitespace cleaning, header standardization, and list formatting.
/// </summary>
public partial class ContentTransformer(
    bool cleanWhitespace,
    bool standardizeHeaders,
    bool fixListFormatting) : BaseContentProcessor
{
    private readonly bool _cleanWhitespace = cleanWhitespace;
    private readonly bool _standardizeHeaders = standardizeHeaders;
    private readonly bool _fixListFormatting = fixListFormatting;

    public override string Name => "content_transformer";

    public override (string Content, NoteMetadata Metadata) Process(
        string content,
        NoteMetadata metadata,
        Dictionary<string, object> context)
    {
        var transformed = content;

        if (_cleanWhitespace)
        {
            transformed = CleanWhitespace(transformed);
        }

        if (_standardizeHeaders)
        {
            transformed = StandardizeHeaders(transformed);
        }

        if (_fixListFormatting)
        {
            transformed = FixListFormatting(transformed);
        }

        return (transformed, metadata);
    }

    private static string CleanWhitespace(string content)
    {
        // Remove trailing whitespace from each line
        var lines = content.Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            lines[i] = lines[i].TrimEnd();
        }
        content = string.Join('\n', lines);

        // Collapse 3+ blank lines to 1 blank line (2 newlines)
        content = ThreeOrMoreBlankLinesRegex().Replace(content, "\n\n");

        return content;
    }

    private static string StandardizeHeaders(string content)
    {
        var lines = content.Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            var line = lines[i];
            // Match markdown headers (# Header)
            var match = HeaderRegex().Match(line);
            if (match.Success)
            {
                var hashes = match.Groups[1].Value;
                var headerText = match.Groups[2].Value.Trim();
                lines[i] = $"{hashes} {headerText}";
            }
        }
        return string.Join('\n', lines);
    }

    private static string FixListFormatting(string content)
    {
        var lines = content.Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            var line = lines[i];

            // Fix dash lists: "-Item" or "-  Item" -> "- Item"
            var dashMatch = DashListRegex().Match(line);
            if (dashMatch.Success)
            {
                var indent = dashMatch.Groups[1].Value;
                var item = dashMatch.Groups[2].Value.Trim();
                lines[i] = $"{indent}- {item}";
            }

            // Fix star lists: "*Item" or "*  Item" -> "* Item"
            var starMatch = StarListRegex().Match(line);
            if (starMatch.Success)
            {
                var indent = starMatch.Groups[1].Value;
                var item = starMatch.Groups[2].Value.Trim();
                lines[i] = $"{indent}* {item}";
            }

            // Fix numbered lists: "1.Item" or "1.  Item" -> "1. Item"
            var numberedMatch = NumberedListRegex().Match(line);
            if (numberedMatch.Success)
            {
                var indent = numberedMatch.Groups[1].Value;
                var number = numberedMatch.Groups[2].Value;
                var item = numberedMatch.Groups[3].Value.Trim();
                lines[i] = $"{indent}{number}. {item}";
            }
        }
        return string.Join('\n', lines);
    }

    [GeneratedRegex(@"\n{3,}")]
    private static partial Regex ThreeOrMoreBlankLinesRegex();

    [GeneratedRegex(@"^(#+)\s*(.+)$")]
    private static partial Regex HeaderRegex();

    [GeneratedRegex(@"^(\s*)-\s*(.+)$")]
    private static partial Regex DashListRegex();

    [GeneratedRegex(@"^(\s*)\*\s*(.+)$")]
    private static partial Regex StarListRegex();

    [GeneratedRegex(@"^(\s*)(\d+)\.\s*(.+)$")]
    private static partial Regex NumberedListRegex();
}
