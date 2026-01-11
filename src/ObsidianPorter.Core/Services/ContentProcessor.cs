namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Models;

/// <summary>
/// Processes SimpleNote .txt files.
/// </summary>
public class ContentProcessor(IFileSystemService fileSystem, IConfigManager configManager) : IContentProcessorService
{
    private readonly string _notesDirectory = configManager.GetNotesDirectory();

    public List<ProcessedNote> ProcessAllNotes()
    {
        if (!fileSystem.DirectoryExists(_notesDirectory))
        {
            return new List<ProcessedNote>();
        }

        var txtFiles = fileSystem.GetFiles(_notesDirectory, "*.txt");
        var notes = new List<ProcessedNote>();

        foreach (var filePath in txtFiles)
        {
            try
            {
                var content = fileSystem.ReadAllText(filePath);
                var title = ExtractTitle(content);
                var filename = Path.GetFileName(filePath);

                // Create basic metadata (will be enriched by MetadataParser if available)
                var metadata = new NoteMetadata(
                    Title: title,
                    Created: DateTime.UtcNow,
                    Modified: DateTime.UtcNow,
                    OriginalId: "",
                    Tags: Array.Empty<string>(),
                    IsMarkdown: false,
                    IsPinned: false,
                    Category: null
                );

                notes.Add(new ProcessedNote(content, metadata, filename));
            }
            catch
            {
                // Skip files that can't be read
                continue;
            }
        }

        return notes;
    }

    public string ExtractTitle(string content)
    {
        var lines = content.Split('\n');
        if (lines.Length == 0 || string.IsNullOrWhiteSpace(lines[0]))
        {
            return "Untitled";
        }

        return lines[0].Trim();
    }
}
