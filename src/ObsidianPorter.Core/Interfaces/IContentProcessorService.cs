namespace ObsidianPorter.Core.Interfaces;

using ObsidianPorter.Core.Models;

/// <summary>
/// Processes SimpleNote .txt files.
/// </summary>
public interface IContentProcessorService
{
    List<ProcessedNote> ProcessAllNotes();
    string ExtractTitle(string content);
}
