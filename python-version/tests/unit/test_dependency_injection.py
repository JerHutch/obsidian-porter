"""
Unit tests for dependency injection refactoring.
Tests the refactored classes with mock file systems.
"""

import json
import pytest
from pathlib import Path

from src.metadata_parser import MetadataParser
from src.content_processor import ContentProcessor
from src.obsidian_formatter import ObsidianFormatter
from src.simplenote_importer import SimpleNoteImporter
from src.interfaces import MockFileSystem
from src.config import ImportConfig


class TestDependencyInjection:
    """Test cases for dependency injection refactoring"""
    
    def test_metadata_parser_with_mock_fs(self, mock_file_system):
        """Test MetadataParser with mock file system"""
        # Setup mock file system
        json_data = {
            "activeNotes": [
                {
                    "id": "test-id-001",
                    "content": "Test Note\nTest content",
                    "creationDate": "2024-01-01T10:00:00.000Z",
                    "lastModified": "2024-01-01T10:30:00.000Z",
                    "tags": ["test"],
                    "systemTags": [],
                    "markdown": False,
                    "pinned": False,
                    "deleted": False
                }
            ],
            "trashedNotes": []
        }
        
        json_path = Path("/test/notes.json")
        mock_file_system.add_file(str(json_path), json.dumps(json_data))
        
        # Test with dependency injection
        parser = MetadataParser(json_path, mock_file_system)
        result = parser.parse()
        
        assert len(result) == 1
        assert "Test Note.txt" in result
        assert result["Test Note.txt"]["original_id"] == "test-id-001"
        assert result["Test Note.txt"]["tags"] == ["test"]
    
    def test_metadata_parser_parse_from_content(self, mock_file_system):
        """Test MetadataParser.parse_from_content method"""
        json_data = {
            "activeNotes": [
                {
                    "id": "test-id-001",
                    "content": "Direct Content Test\nDirect content",
                    "creationDate": "2024-01-01T10:00:00.000Z",
                    "tags": ["direct"]
                }
            ]
        }
        
        parser = MetadataParser(Path("/dummy.json"), mock_file_system)
        result = parser.parse_from_content(json.dumps(json_data))
        
        assert len(result) == 1
        assert "Direct Content Test.txt" in result
        assert result["Direct Content Test.txt"]["original_id"] == "test-id-001"
    
    def test_content_processor_with_mock_fs(self, mock_file_system):
        """Test ContentProcessor with mock file system"""
        # Setup mock file system
        notes_dir = Path("/test/notes")
        mock_file_system.add_directory(str(notes_dir))
        mock_file_system.add_file(str(notes_dir / "note1.txt"), "Note One\nContent of note one")
        mock_file_system.add_file(str(notes_dir / "note2.txt"), "Note Two\nContent of note two")
        mock_file_system.add_file(str(notes_dir / "not_txt.md"), "Should be ignored")
        
        # Test with dependency injection
        processor = ContentProcessor(notes_dir, mock_file_system)
        
        # Test get_txt_files
        txt_files = processor.get_txt_files()
        assert len(txt_files) == 2
        filenames = [f.name for f in txt_files]
        assert "note1.txt" in filenames
        assert "note2.txt" in filenames
        assert "not_txt.md" not in filenames
        
        # Test read_note_content
        content = processor.read_note_content(notes_dir / "note1.txt")
        assert content == "Note One\nContent of note one"
        
        # Test get_note_data
        note_data = processor.get_note_data(notes_dir / "note1.txt")
        assert note_data["title"] == "Note One"
        assert note_data["content"] == "Note One\nContent of note one"
        assert note_data["filename"] == "note1.txt"
    
    def test_obsidian_formatter_with_mock_fs(self, mock_file_system):
        """Test ObsidianFormatter with mock file system"""
        output_dir = Path("/test/output")
        mock_file_system.add_directory(str(output_dir))
        
        formatter = ObsidianFormatter(output_dir, mock_file_system)
        
        note_data = {
            "title": "Test Note",
            "content": "Test content"
        }
        
        metadata = {
            "original_id": "test-123",
            "tags": ["test"],
            "created": "2024-01-01T10:00:00.000Z"
        }
        
        # Test format_note (doesn't require file system)
        formatted = formatter.format_note(note_data, metadata)
        assert "title: Test Note" in formatted
        assert "original_id: test-123" in formatted
        assert "Test content" in formatted
        
        # Test save_note
        saved_path = formatter.save_note(note_data, metadata)
        assert saved_path == output_dir / "Test Note.md"
        
        # Verify file was written to mock file system
        assert mock_file_system.exists(saved_path)
        saved_content = mock_file_system.read_text(saved_path)
        assert "title: Test Note" in saved_content
        assert "Test content" in saved_content
    
    def test_obsidian_formatter_folder_organization(self, mock_file_system):
        """Test ObsidianFormatter folder organization with mock file system"""
        output_dir = Path("/test/output")
        mock_file_system.add_directory(str(output_dir))
        
        formatter = ObsidianFormatter(output_dir, mock_file_system)
        
        note_data = {
            "title": "Project Note",
            "content": "Project content"
        }
        
        metadata = {
            "_folder_path": "Projects/Work",
            "tags": ["project"]
        }
        
        saved_path = formatter.save_note(note_data, metadata)
        expected_path = output_dir / "Projects" / "Work" / "Project Note.md"
        
        assert saved_path == expected_path
        assert mock_file_system.exists(expected_path)
        
        # Verify directories were created
        assert mock_file_system.is_dir(output_dir / "Projects")
        assert mock_file_system.is_dir(output_dir / "Projects" / "Work")
    
    def test_simplenote_importer_with_mock_fs(self, mock_file_system):
        """Test SimpleNoteImporter with dependency injection"""
        # Setup mock file system
        notes_dir = Path("/test/notes")
        json_path = notes_dir / "source" / "notes.json"
        output_dir = Path("/test/output")
        
        # Add directories
        mock_file_system.add_directory(str(notes_dir))
        mock_file_system.add_directory(str(notes_dir / "source"))
        mock_file_system.add_directory(str(output_dir))
        
        # Add test files
        mock_file_system.add_file(str(notes_dir / "test_note.txt"), "Test Note\nTest content")
        
        json_data = {
            "activeNotes": [
                {
                    "id": "test-id-001",
                    "content": "Test Note\nTest content",
                    "creationDate": "2024-01-01T10:00:00.000Z",
                    "tags": ["test"]
                }
            ]
        }
        mock_file_system.add_file(str(json_path), json.dumps(json_data))
        
        # Test with dependency injection
        config = ImportConfig(enable_editor_pipeline=False)
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            json_path=json_path,
            output_directory=output_dir,
            config=config,
            file_system=mock_file_system
        )
        
        # Verify components were initialized with mock file system
        assert importer.file_system == mock_file_system
        assert importer.content_processor.file_system == mock_file_system
        assert importer.obsidian_formatter.file_system == mock_file_system
        assert importer.metadata_parser.file_system == mock_file_system
    
    def test_file_system_isolation(self, mock_file_system):
        """Test that mock file system provides proper isolation"""
        # Test that different instances are isolated
        fs1 = MockFileSystem()
        fs2 = MockFileSystem()
        
        fs1.add_file("/test/file1.txt", "Content 1")
        fs2.add_file("/test/file2.txt", "Content 2")
        
        assert fs1.exists(Path("/test/file1.txt"))
        assert not fs1.exists(Path("/test/file2.txt"))
        
        assert fs2.exists(Path("/test/file2.txt"))
        assert not fs2.exists(Path("/test/file1.txt"))
    
    def test_mock_file_system_error_handling(self, mock_file_system):
        """Test mock file system error handling"""
        # Test reading non-existent file
        with pytest.raises(FileNotFoundError):
            mock_file_system.read_text(Path("/nonexistent.txt"))
        
        # Test creating directory that already exists without exist_ok
        mock_file_system.add_directory("/test")
        with pytest.raises(FileExistsError):
            mock_file_system.mkdir(Path("/test"), exist_ok=False)
    
    def test_backward_compatibility(self, temp_dir):
        """Test that refactored classes still work without dependency injection"""
        # Test that classes work with default file system (None passed)
        json_path = temp_dir / "test.json"
        notes_dir = temp_dir / "notes"
        output_dir = temp_dir / "output"
        
        notes_dir.mkdir()
        
        # Create test files
        test_note = notes_dir / "test.txt"
        test_note.write_text("Test Note\nTest content")
        
        json_data = {
            "activeNotes": [
                {
                    "id": "test-001",
                    "content": "Test Note\nTest content",
                    "creationDate": "2024-01-01T10:00:00.000Z"
                }
            ]
        }
        json_path.write_text(json.dumps(json_data))
        
        # Test without explicit file system (should use RealFileSystem)
        parser = MetadataParser(json_path)
        result = parser.parse()
        assert len(result) == 1
        
        processor = ContentProcessor(notes_dir)
        notes = processor.process_all_notes()
        assert len(notes) == 1
        
        formatter = ObsidianFormatter(output_dir)
        formatted = formatter.format_note(notes[0])
        assert "title: Test Note" in formatted