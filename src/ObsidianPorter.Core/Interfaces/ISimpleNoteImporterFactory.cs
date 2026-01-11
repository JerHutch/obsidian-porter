namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Factory for creating SimpleNoteImporter instances with runtime parameters.
/// </summary>
public interface ISimpleNoteImporterFactory
{
    ISimpleNoteImporter Create(
        ImportConfig config,
        string notesDirectory,
        string jsonPath,
        string outputDirectory);
}
