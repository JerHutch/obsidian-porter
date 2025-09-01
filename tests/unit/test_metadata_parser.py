"""
Unit tests for MetadataParser class.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

from src.metadata_parser import MetadataParser


class TestMetadataParser:
    """Test cases for MetadataParser class"""
    
    def test_init(self, temp_dir):
        """Test MetadataParser initialization"""
        json_path = temp_dir / "test.json"
        parser = MetadataParser(json_path)
        
        assert parser.json_path == json_path
        assert parser.metadata_map == {}
    
    def test_parse_basic_metadata(self, temp_dir, basic_metadata_json):
        """Test parsing basic metadata JSON"""
        json_path = temp_dir / "basic.json"
        with open(json_path, 'w') as f:
            json.dump(basic_metadata_json, f)
        
        parser = MetadataParser(json_path)
        result = parser.parse()
        
        assert len(result) == 2
        assert "My First Test Note.txt" in result
        assert "Empty Note Title.txt" in result
        
        # Check first note metadata
        first_note = result["My First Test Note.txt"]
        assert first_note['original_id'] == "test-id-001"
        assert first_note['source'] == "simplenote"
        assert first_note['tags'] == []
        assert first_note['markdown'] is False
        assert first_note['pinned'] is False
    
    def test_parse_complex_metadata(self, temp_dir, complex_metadata_json):
        """Test parsing complex metadata with tags and formatting"""
        json_path = temp_dir / "complex.json"
        with open(json_path, 'w') as f:
            json.dump(complex_metadata_json, f)
        
        parser = MetadataParser(json_path)
        result = parser.parse()
        
        assert len(result) == 3
        
        # Check project note
        project_note = result["Project Planning and Ideas.txt"]
        assert project_note['original_id'] == "test-id-003"
        assert project_note['tags'] == ["project", "planning", "development", "meeting", "budget"]
        assert project_note['markdown'] is True
        assert project_note['pinned'] is True
    
    def test_parse_edge_cases(self, temp_dir, edge_cases_json):
        """Test parsing edge cases and problematic data"""
        json_path = temp_dir / "edge_cases.json"
        with open(json_path, 'w') as f:
            json.dump(edge_cases_json, f)
        
        parser = MetadataParser(json_path)
        result = parser.parse()
        
        # Should only process active notes, not deleted ones
        assert len(result) == 2  # Empty content note is skipped, very long name note is included
        
        # Check that note with null tags is handled properly
        note_with_null_tags = None
        for filename, metadata in result.items():
            if metadata['original_id'] == "test-id-edge-002":
                note_with_null_tags = metadata
                break
        
        assert note_with_null_tags is not None
        assert note_with_null_tags['tags'] is None
    
    def test_parse_invalid_json_file(self, temp_dir):
        """Test handling of invalid JSON file"""
        json_path = temp_dir / "invalid.json"
        with open(json_path, 'w') as f:
            f.write("{ invalid json }")
        
        parser = MetadataParser(json_path)
        
        with pytest.raises(json.JSONDecodeError):
            parser.parse()
    
    def test_parse_missing_file(self, temp_dir):
        """Test handling of missing JSON file"""
        json_path = temp_dir / "missing.json"
        parser = MetadataParser(json_path)
        
        with pytest.raises(FileNotFoundError):
            parser.parse()
    
    def test_extract_metadata(self, temp_dir):
        """Test metadata extraction from individual note"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        note_data = {
            'id': 'test-123',
            'creationDate': '2024-01-01T10:00:00.000Z',
            'modificationDate': '2024-01-01T11:00:00.000Z',
            'tags': ['test', 'sample'],
            'markdown': True,
            'pinned': False
        }
        
        result = parser._extract_metadata(note_data)
        
        assert result['original_id'] == 'test-123'
        assert isinstance(result['created'], datetime)
        assert isinstance(result['modified'], datetime)
        assert result['tags'] == ['test', 'sample']
        assert result['markdown'] is True
        assert result['pinned'] is False
        assert result['source'] == 'simplenote'
    
    def test_parse_timestamp_valid(self, temp_dir):
        """Test parsing valid timestamp strings"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        # Test ISO format
        result = parser._parse_timestamp('2024-01-01T10:00:00.000Z')
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
        
        # Test different format
        result = parser._parse_timestamp('2024-01-01 10:00:00')
        assert isinstance(result, datetime)
    
    def test_parse_timestamp_invalid(self, temp_dir):
        """Test handling of invalid timestamp strings"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        # Test invalid format
        result = parser._parse_timestamp('invalid-date')
        assert result is None
        
        # Test None input
        result = parser._parse_timestamp(None)
        assert result is None
        
        # Test empty string
        result = parser._parse_timestamp('')
        assert result is None
    
    def test_generate_filename_basic(self, temp_dir):
        """Test filename generation from content"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        content = "This is the title\nThis is the content"
        result = parser._generate_filename(content)
        
        assert result == "This is the title.txt"
    
    def test_generate_filename_markdown_header(self, temp_dir):
        """Test filename generation with markdown headers"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        content = "# Markdown Title\nContent here"
        result = parser._generate_filename(content)
        
        assert result == "Markdown Title.txt"
        
        content = "## Sub Header\nContent here"
        result = parser._generate_filename(content)
        
        assert result == "Sub Header.txt"
    
    def test_generate_filename_empty_content(self, temp_dir):
        """Test filename generation with empty content"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        # Empty string
        result = parser._generate_filename("")
        assert result is None
        
        # Only whitespace
        result = parser._generate_filename("   \n  \t  ")
        assert result is None
    
    def test_generate_filename_empty_first_line(self, temp_dir):
        """Test filename generation with empty first line"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        content = "\n\nActual content here"
        result = parser._generate_filename(content)
        assert result is None
        
        content = "#  \nActual content"
        result = parser._generate_filename(content)
        assert result is None
    
    def test_sanitize_filename_special_chars(self, temp_dir):
        """Test filename sanitization with special characters"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        # Test invalid filename characters
        result = parser._sanitize_filename('Invalid<>:"/\\|?*Name')
        assert result == "Invalid_________Name"
        
        # Test normal characters
        result = parser._sanitize_filename('Normal File Name 123')
        assert result == "Normal File Name 123"
    
    def test_sanitize_filename_length_limit(self, temp_dir):
        """Test filename length limiting"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        long_name = "A" * 150  # 150 characters
        result = parser._sanitize_filename(long_name)
        
        assert len(result) == 100
        assert result == "A" * 100
    
    def test_sanitize_filename_whitespace(self, temp_dir):
        """Test filename whitespace handling"""
        parser = MetadataParser(temp_dir / "dummy.json")
        
        result = parser._sanitize_filename("  Title with spaces  ")
        assert result == "Title with spaces"
        
        result = parser._sanitize_filename("   ")
        assert result == "untitled"
    
    def test_get_metadata_for_file(self, temp_dir, basic_metadata_json):
        """Test retrieving metadata for specific file"""
        json_path = temp_dir / "basic.json"
        with open(json_path, 'w') as f:
            json.dump(basic_metadata_json, f)
        
        parser = MetadataParser(json_path)
        parser.parse()
        
        # Test existing file
        metadata = parser.get_metadata_for_file("My First Test Note.txt")
        assert metadata is not None
        assert metadata['original_id'] == "test-id-001"
        
        # Test non-existing file
        metadata = parser.get_metadata_for_file("Non Existing Note.txt")
        assert metadata is None
    
    @pytest.mark.edge_case
    def test_parse_malformed_note_structure(self, temp_dir):
        """Test parsing with malformed note structure"""
        malformed_data = {
            "activeNotes": [
                {
                    "id": "test-1",
                    "content": "Valid note"
                    # Missing required fields
                },
                {
                    # Missing id field
                    "content": "Another note",
                    "creationDate": "2024-01-01T10:00:00.000Z"
                }
            ]
        }
        
        json_path = temp_dir / "malformed.json"
        with open(json_path, 'w') as f:
            json.dump(malformed_data, f)
        
        parser = MetadataParser(json_path)
        result = parser.parse()
        
        # Should handle missing fields gracefully
        assert len(result) == 2
        
        for metadata in result.values():
            # Should have default values for missing fields
            assert 'original_id' in metadata
            assert 'source' in metadata
            assert metadata['source'] == 'simplenote'