namespace ObsidianPorter.Tests.Interfaces;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;

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
