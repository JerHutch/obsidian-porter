namespace ObsidianPorter.Core.Services;

using ObsidianPorter.Core.Interfaces;

/// <summary>
/// Real file system implementation.
/// </summary>
public class FileSystemService : IFileSystemService
{
    public bool FileExists(string path) => File.Exists(path);

    public bool DirectoryExists(string path) => Directory.Exists(path);

    public string ReadAllText(string path) => File.ReadAllText(path);

    public void WriteAllText(string path, string content) => File.WriteAllText(path, content);

    public void CreateDirectory(string path) => Directory.CreateDirectory(path);

    public IEnumerable<string> GetFiles(string path, string searchPattern) =>
        Directory.GetFiles(path, searchPattern);

    public bool IsFile(string path) => File.Exists(path) && !Directory.Exists(path);

    public bool IsDirectory(string path) => Directory.Exists(path);
}
