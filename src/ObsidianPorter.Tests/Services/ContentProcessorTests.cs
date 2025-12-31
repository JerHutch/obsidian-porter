namespace ObsidianPorter.Tests.Services;

using Shouldly;
using NSubstitute;
using ObsidianPorter.Core.Interfaces;
using ObsidianPorter.Core.Services;

public class ContentProcessorTests
{
    [Test]
    public void ProcessAllNotes_FindsAndProcessesTxtFiles()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.DirectoryExists("/notes").Returns(true);
        fs.GetFiles("/notes", "*.txt").Returns(new[] { "/notes/note1.txt", "/notes/note2.txt" });
        fs.ReadAllText("/notes/note1.txt").Returns("First Note\nContent here");
        fs.ReadAllText("/notes/note2.txt").Returns("Second Note\nMore content");

        var processor = new ContentProcessor(fs, "/notes");
        var notes = processor.ProcessAllNotes();

        notes.Count.ShouldBe(2);
        notes[0].Content.ShouldContain("First Note");
        notes[1].Content.ShouldContain("Second Note");
    }

    [Test]
    public void ProcessAllNotes_WhenNoFiles_ReturnsEmpty()
    {
        var fs = Substitute.For<IFileSystemService>();
        fs.DirectoryExists("/notes").Returns(true);
        fs.GetFiles("/notes", "*.txt").Returns(Array.Empty<string>());

        var processor = new ContentProcessor(fs, "/notes");
        var notes = processor.ProcessAllNotes();

        notes.ShouldBeEmpty();
    }

    [Test]
    public void ExtractTitle_FromFirstLine_ReturnsTitle()
    {
        var fs = Substitute.For<IFileSystemService>();
        var processor = new ContentProcessor(fs, "/notes");

        var title = processor.ExtractTitle("My Note Title\nContent here\nMore content");

        title.ShouldBe("My Note Title");
    }
}
