namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Parses metadata from SimpleNote JSON export.
/// </summary>
public interface IMetadataParser
{
    Dictionary<string, NoteMetadata> Parse();
}
