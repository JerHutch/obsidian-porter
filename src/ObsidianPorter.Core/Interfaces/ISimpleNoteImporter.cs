namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Main orchestrator for importing SimpleNote exports to Obsidian.
/// </summary>
public interface ISimpleNoteImporter
{
    ImportResult Import();
}
