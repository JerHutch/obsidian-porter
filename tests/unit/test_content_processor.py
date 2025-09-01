"""
Unit tests for ContentProcessor class.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.content_processor import ContentProcessor


class TestContentProcessor:
    """Test cases for ContentProcessor class"""
    
    def test_init(self, temp_dir):
        """Test ContentProcessor initialization"""
        processor = ContentProcessor(temp_dir)
        
        assert processor.notes_directory == Path(temp_dir)
    
    def test_get_txt_files(self, temp_dir):
        """Test finding .txt files in directory"""
        # Create test files
        (temp_dir / "note1.txt").write_text("Content 1")
        (temp_dir / "note2.txt").write_text("Content 2")
        (temp_dir / "not_txt.md").write_text("Not a txt file")
        
        processor = ContentProcessor(temp_dir)
        txt_files = processor.get_txt_files()
        
        assert len(txt_files) == 2
        filenames = [f.name for f in txt_files]
        assert "note1.txt" in filenames
        assert "note2.txt" in filenames
        assert "not_txt.md" not in filenames
    
    def test_get_txt_files_empty_directory(self, temp_dir):
        """Test finding txt files in empty directory"""
        processor = ContentProcessor(temp_dir)
        txt_files = processor.get_txt_files()
        
        assert len(txt_files) == 0
    
    def test_get_txt_files_nonexistent_directory(self, temp_dir):
        """Test handling of nonexistent directory"""
        nonexistent_dir = temp_dir / "does_not_exist"
        processor = ContentProcessor(nonexistent_dir)
        
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            processor.get_txt_files()
    
    def test_read_note_content(self, temp_dir, simple_note_content):
        """Test reading note content from file"""
        note_file = temp_dir / "test_note.txt"
        note_file.write_text(simple_note_content, encoding='utf-8')
        
        processor = ContentProcessor(temp_dir)
        content = processor.read_note_content(note_file)
        
        assert content == simple_note_content.strip()
    
    def test_read_note_content_with_encoding(self, temp_dir, special_chars_content):
        """Test reading note content with special characters"""
        note_file = temp_dir / "special_chars.txt"
        note_file.write_text(special_chars_content, encoding='utf-8')
        
        processor = ContentProcessor(temp_dir)
        content = processor.read_note_content(note_file)
        
        assert content == special_chars_content.strip()
        assert "café" in content
        assert "résumé" in content
    
    def test_read_note_content_nonexistent_file(self, temp_dir):
        """Test reading from nonexistent file"""
        processor = ContentProcessor(temp_dir)
        nonexistent_file = temp_dir / "does_not_exist.txt"
        
        content = processor.read_note_content(nonexistent_file)
        assert content is None
    
    def test_read_note_content_empty_file(self, temp_dir):
        """Test reading empty file"""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        
        processor = ContentProcessor(temp_dir)
        content = processor.read_note_content(empty_file)
        
        assert content == ""
    
    def test_extract_title_basic(self, temp_dir):
        """Test title extraction from basic content"""
        processor = ContentProcessor(temp_dir)
        
        content = "This is the title\nThis is the body content"
        title = processor.extract_title(content)
        
        assert title == "This is the title"
    
    def test_extract_title_markdown_headers(self, temp_dir):
        """Test title extraction from markdown headers"""
        processor = ContentProcessor(temp_dir)
        
        # H1 header
        content = "# Main Title\nContent here"
        title = processor.extract_title(content)
        assert title == "Main Title"
        
        # H2 header
        content = "## Sub Title\nContent here"
        title = processor.extract_title(content)
        assert title == "Sub Title"
        
        # H3 header with multiple #
        content = "### Small Title\nContent here"
        title = processor.extract_title(content)
        assert title == "Small Title"
    
    def test_extract_title_empty_content(self, temp_dir):
        """Test title extraction from empty content"""
        processor = ContentProcessor(temp_dir)
        
        # Empty string
        title = processor.extract_title("")
        assert title == "Untitled"
        
        # Only whitespace
        title = processor.extract_title("   \n  \t  ")
        assert title == "Untitled"
    
    def test_extract_title_empty_first_line(self, temp_dir):
        """Test title extraction with empty first line"""
        processor = ContentProcessor(temp_dir)
        
        # Empty first line - should take first non-empty line after strip()
        content = "\n\nActual content"
        title = processor.extract_title(content)
        assert title == "Actual content"
        
        # Empty markdown header
        content = "#  \nActual content"
        title = processor.extract_title(content)
        assert title == "Untitled"
    
    def test_extract_title_whitespace_handling(self, temp_dir):
        """Test title extraction with whitespace"""
        processor = ContentProcessor(temp_dir)
        
        content = "  Title with spaces  \nContent"
        title = processor.extract_title(content)
        assert title == "Title with spaces"
        
        content = "#   Markdown Title   \nContent"
        title = processor.extract_title(content)
        assert title == "Markdown Title"
    
    def test_process_content_basic(self, temp_dir):
        """Test basic content processing (Phase 1)"""
        processor = ContentProcessor(temp_dir)
        
        content = "  Title\n\nBody content\nMore content  "
        processed = processor.process_content(content)
        
        # Phase 1: Just strips whitespace
        expected = "Title\n\nBody content\nMore content"
        assert processed == expected
    
    def test_process_content_empty(self, temp_dir):
        """Test processing empty content"""
        processor = ContentProcessor(temp_dir)
        
        processed = processor.process_content("")
        assert processed == ""
        
        processed = processor.process_content("   \n  \t  ")
        assert processed == ""
    
    def test_get_note_data(self, temp_dir, simple_note_content):
        """Test getting complete note data"""
        note_file = temp_dir / "test_note.txt"
        note_file.write_text(simple_note_content)
        
        processor = ContentProcessor(temp_dir)
        note_data = processor.get_note_data(note_file)
        
        assert note_data is not None
        assert note_data['filename'] == "test_note.txt"
        assert note_data['title'] == "My First Test Note"
        assert note_data['content'] == simple_note_content.strip()
        assert note_data['original_path'] == note_file
    
    def test_get_note_data_nonexistent_file(self, temp_dir):
        """Test getting note data for nonexistent file"""
        processor = ContentProcessor(temp_dir)
        nonexistent_file = temp_dir / "missing.txt"
        
        note_data = processor.get_note_data(nonexistent_file)
        assert note_data is None
    
    def test_get_note_data_complex_content(self, temp_dir, complex_note_content):
        """Test getting note data for complex content"""
        note_file = temp_dir / "complex_note.txt"
        note_file.write_text(complex_note_content)
        
        processor = ContentProcessor(temp_dir)
        note_data = processor.get_note_data(note_file)
        
        assert note_data is not None
        assert note_data['filename'] == "complex_note.txt"
        assert note_data['title'] == "Project Planning and Ideas"
        assert "## Sprint Goals" in note_data['content']
        assert note_data['original_path'] == note_file
    
    def test_process_all_notes(self, temp_dir, simple_note_content, complex_note_content):
        """Test processing all notes in directory"""
        # Create multiple test files
        (temp_dir / "note1.txt").write_text(simple_note_content)
        (temp_dir / "note2.txt").write_text(complex_note_content)
        (temp_dir / "note3.txt").write_text("Simple Note\nSimple content")
        (temp_dir / "not_txt.md").write_text("Should be ignored")
        
        processor = ContentProcessor(temp_dir)
        notes = processor.process_all_notes()
        
        assert len(notes) == 3
        
        # Check that all notes have required fields
        for note in notes:
            assert 'filename' in note
            assert 'title' in note
            assert 'content' in note
            assert 'original_path' in note
            assert note['filename'].endswith('.txt')
    
    def test_process_all_notes_empty_directory(self, temp_dir):
        """Test processing all notes in empty directory"""
        processor = ContentProcessor(temp_dir)
        notes = processor.process_all_notes()
        
        assert len(notes) == 0
    
    def test_process_all_notes_with_errors(self, temp_dir):
        """Test processing notes when some files have errors"""
        # Create valid file
        (temp_dir / "valid.txt").write_text("Valid Note\nContent")
        
        # Create file that will cause read error (simulate by using mock)
        (temp_dir / "problematic.txt").write_text("Content")
        
        processor = ContentProcessor(temp_dir)
        
        # Mock read_note_content to return None for problematic file
        original_read = processor.read_note_content
        def mock_read(file_path):
            if file_path.name == "problematic.txt":
                return None
            return original_read(file_path)
        
        processor.read_note_content = mock_read
        
        notes = processor.process_all_notes()
        
        # Should process only the valid file
        assert len(notes) == 1
        assert notes[0]['filename'] == "valid.txt"
    
    @pytest.mark.edge_case
    def test_extract_title_very_long_first_line(self, temp_dir):
        """Test title extraction with very long first line"""
        processor = ContentProcessor(temp_dir)
        
        long_title = "A" * 1000
        content = f"{long_title}\nContent"
        
        title = processor.extract_title(content)
        assert title == long_title  # ContentProcessor doesn't limit length
    
    @pytest.mark.edge_case
    def test_extract_title_with_special_characters(self, temp_dir):
        """Test title extraction with special characters"""
        processor = ContentProcessor(temp_dir)
        
        content = "Title with special chars: <>:\"/\\|?*\nContent"
        title = processor.extract_title(content)
        
        assert title == "Title with special chars: <>:\"/\\|?*"
    
    @pytest.mark.edge_case
    def test_read_note_content_large_file(self, temp_dir):
        """Test reading very large file"""
        large_content = "Line\n" * 10000  # 10k lines
        large_file = temp_dir / "large.txt"
        large_file.write_text(large_content)
        
        processor = ContentProcessor(temp_dir)
        content = processor.read_note_content(large_file)
        
        assert content is not None
        assert len(content.split('\n')) == 10000