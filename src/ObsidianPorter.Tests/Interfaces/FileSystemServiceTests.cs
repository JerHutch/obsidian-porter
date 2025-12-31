namespace ObsidianPorter.Tests.Interfaces;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;
using System.IO;

public class FileSystemServiceTests
{
    [Test]
    public void FileExists_WhenFileMissing_ReturnsFalse()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.FileExists(Arg.Any<string>()).Returns(false);

        var result = fs.FileExists("/fake/path.txt");

        result.ShouldBeFalse();
    }

    [Test]
    public void ReadAllText_ReturnsFileContent()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.ReadAllText(Arg.Any<string>()).Returns("File content");

        var result = fs.ReadAllText("/fake/file.txt");

        result.ShouldBe("File content");
    }
}

public class FileSystemServiceRealTests
{
    private string _testDir = null!;
    private FileSystemService _fs = null!;

    [SetUp]
    public void SetUp()
    {
        _testDir = Path.Combine(Path.GetTempPath(), $"obsidian-porter-test-{Guid.NewGuid()}");
        Directory.CreateDirectory(_testDir);
        _fs = new FileSystemService();
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_testDir))
        {
            Directory.Delete(_testDir, recursive: true);
        }
    }

    [Test]
    public void FileExists_WhenFileExists_ReturnsTrue()
    {
        var testFile = Path.Combine(_testDir, "test.txt");
        File.WriteAllText(testFile, "content");

        var result = _fs.FileExists(testFile);

        result.ShouldBeTrue();
    }

    [Test]
    public void ReadAllText_ReturnsFileContent()
    {
        var testFile = Path.Combine(_testDir, "test.txt");
        File.WriteAllText(testFile, "Hello World");

        var content = _fs.ReadAllText(testFile);

        content.ShouldBe("Hello World");
    }

    [Test]
    public void WriteAllText_CreatesFileWithContent()
    {
        var testFile = Path.Combine(_testDir, "output.txt");

        _fs.WriteAllText(testFile, "Test Content");

        File.Exists(testFile).ShouldBeTrue();
        File.ReadAllText(testFile).ShouldBe("Test Content");
    }

    [Test]
    public void GetFiles_ReturnsMatchingFiles()
    {
        File.WriteAllText(Path.Combine(_testDir, "note1.txt"), "");
        File.WriteAllText(Path.Combine(_testDir, "note2.txt"), "");
        File.WriteAllText(Path.Combine(_testDir, "other.md"), "");

        var files = _fs.GetFiles(_testDir, "*.txt");

        files.Count().ShouldBe(2);
        files.ShouldAllBe(f => f.EndsWith(".txt"));
    }
}
