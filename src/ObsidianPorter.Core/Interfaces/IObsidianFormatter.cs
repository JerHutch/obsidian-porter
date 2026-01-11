namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Formats notes as Obsidian-compatible markdown with YAML frontmatter.
/// </summary>
public interface IObsidianFormatter
{
    void FormatAndSave(string content, NoteMetadata metadata, Dictionary<string, object> context);
}
