namespace ObsidianPorter.Core.Interfaces;

/// <summary>
/// Abstraction for file system operations to enable testing.
/// </summary>
public interface IFileSystemService
{
    bool FileExists(string path);
    bool DirectoryExists(string path);
    string ReadAllText(string path);
    void WriteAllText(string path, string content);
    void CreateDirectory(string path);
    IEnumerable<string> GetFiles(string path, string searchPattern);
    bool IsFile(string path);
    bool IsDirectory(string path);
}
