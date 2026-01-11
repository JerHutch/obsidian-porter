"""
Unit tests for ObsidianFormatter class.
"""

import pytest
import yaml
from datetime import datetime
from pathlib import Path

from src.obsidian_formatter import ObsidianFormatter


class TestObsidianFormatter:
    """Test cases for ObsidianFormatter class"""
    
    def test_init(self, temp_dir):
        """Test ObsidianFormatter initialization"""
        output_dir = temp_dir / "output"
        formatter = ObsidianFormatter(output_dir)
        
        assert formatter.output_directory == output_dir
        assert output_dir.exists()  # Should create directory
    
    def test_init_existing_directory(self, temp_dir):
        """Test initialization with existing directory"""
        output_dir = temp_dir / "existing"
        output_dir.mkdir()
        
        formatter = ObsidianFormatter(output_dir)
        assert formatter.output_directory == output_dir
    
    def test_format_note_basic(self, temp_dir, sample_note_data):
        """Test basic note formatting"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Test Note',
            'content': 'This is test content'
        }
        
        formatted = formatter.format_note(note_data)
        
        # Should contain YAML frontmatter
        assert formatted.startswith('---\n')
        assert '---\n\n' in formatted
        assert 'title: Test Note' in formatted
        assert 'source: simplenote' in formatted
        assert 'This is test content' in formatted
    
    def test_format_note_with_metadata(self, temp_dir):
        """Test note formatting with metadata"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Test Note',
            'content': 'Test content'
        }
        
        metadata = {
            'original_id': 'test-123',
            'created': datetime(2024, 1, 1, 10, 0, 0),
            'modified': datetime(2024, 1, 1, 11, 0, 0),
            'tags': ['test', 'sample'],
            'markdown': True,
            'pinned': False
        }
        
        formatted = formatter.format_note(note_data, metadata)
        
        assert 'original_id: test-123' in formatted
        assert 'created: 2024-01-01T10:00:00' in formatted
        assert 'modified: 2024-01-01T11:00:00' in formatted
        assert 'tags:' in formatted
        assert '- test' in formatted
        assert '- sample' in formatted
        assert 'markdown: true' in formatted
        assert 'pinned: false' in formatted
    
    def test_create_frontmatter_minimal(self, temp_dir):
        """Test frontmatter creation with minimal data"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {'title': 'Simple Note'}
        frontmatter = formatter._create_frontmatter(note_data, None)
        
        assert frontmatter['title'] == 'Simple Note'
        assert frontmatter['source'] == 'simplenote'
        assert frontmatter['tags'] == []
    
    def test_create_frontmatter_full_metadata(self, temp_dir):
        """Test frontmatter creation with full metadata"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {'title': 'Test Note'}
        metadata = {
            'original_id': 'abc-123',
            'created': datetime(2024, 1, 1),
            'modified': datetime(2024, 1, 2),
            'tags': ['important', 'work'],
            'markdown': True,
            'pinned': True
        }
        
        frontmatter = formatter._create_frontmatter(note_data, metadata)
        
        assert frontmatter['title'] == 'Test Note'
        assert frontmatter['source'] == 'simplenote'
        assert frontmatter['original_id'] == 'abc-123'
        assert frontmatter['created'] == '2024-01-01T00:00:00'
        assert frontmatter['modified'] == '2024-01-02T00:00:00'
        assert frontmatter['tags'] == ['important', 'work']
        assert frontmatter['markdown'] is True
        assert frontmatter['pinned'] is True
    
    def test_create_frontmatter_partial_metadata(self, temp_dir):
        """Test frontmatter creation with partial metadata"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {'title': 'Test Note'}
        metadata = {
            'original_id': 'test-123',
            'tags': ['test']
            # Missing created, modified, etc.
        }
        
        frontmatter = formatter._create_frontmatter(note_data, metadata)
        
        assert frontmatter['title'] == 'Test Note'
        assert frontmatter['original_id'] == 'test-123'
        assert frontmatter['tags'] == ['test']
        assert 'created' not in frontmatter
        assert 'modified' not in frontmatter
    
    def test_format_datetime(self, temp_dir):
        """Test datetime formatting"""
        formatter = ObsidianFormatter(temp_dir)
        
        dt = datetime(2024, 1, 15, 14, 30, 45)
        formatted = formatter._format_datetime(dt)
        
        assert formatted == '2024-01-15T14:30:45'
    
    def test_format_datetime_non_datetime(self, temp_dir):
        """Test datetime formatting with non-datetime input"""
        formatter = ObsidianFormatter(temp_dir)
        
        formatted = formatter._format_datetime('not-a-datetime')
        assert formatted == 'not-a-datetime'
    
    def test_sanitize_filename_basic(self, temp_dir):
        """Test basic filename sanitization"""
        formatter = ObsidianFormatter(temp_dir)
        
        result = formatter._sanitize_filename('Normal Title')
        assert result == 'Normal Title'
    
    def test_sanitize_filename_invalid_chars(self, temp_dir):
        """Test sanitization of invalid characters"""
        formatter = ObsidianFormatter(temp_dir)
        
        result = formatter._sanitize_filename('Invalid<>:"/\\|?*Title')
        assert result == 'Invalid_________Title'
    
    def test_sanitize_filename_obsidian_chars(self, temp_dir):
        """Test sanitization of Obsidian-problematic characters"""
        formatter = ObsidianFormatter(temp_dir)
        
        result = formatter._sanitize_filename('Title [with] brackets')
        assert result == 'Title (with) brackets'
    
    def test_sanitize_filename_length_limit(self, temp_dir):
        """Test filename length limiting"""
        formatter = ObsidianFormatter(temp_dir)
        
        long_title = 'A' * 150
        result = formatter._sanitize_filename(long_title)
        
        assert len(result) == 100
        assert result == 'A' * 100
    
    def test_sanitize_filename_whitespace(self, temp_dir):
        """Test filename whitespace handling"""
        formatter = ObsidianFormatter(temp_dir)
        
        result = formatter._sanitize_filename('  Title with spaces  ')
        assert result == 'Title with spaces'
        
        result = formatter._sanitize_filename('   ')
        assert result == 'untitled'
    
    def test_generate_filename(self, temp_dir):
        """Test filename generation"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {'title': 'My Test Note'}
        filename = formatter.generate_filename(note_data)
        
        assert filename == 'My Test Note.md'
    
    def test_generate_filename_no_title(self, temp_dir):
        """Test filename generation without title"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {}
        filename = formatter.generate_filename(note_data)
        
        assert filename == 'Untitled.md'
    
    def test_generate_filename_special_chars(self, temp_dir):
        """Test filename generation with special characters"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {'title': 'Title/With\\Special:Chars'}
        filename = formatter.generate_filename(note_data)
        
        assert filename == 'Title_With_Special_Chars.md'
    
    def test_save_note_basic(self, temp_dir):
        """Test saving a basic note"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Test Note',
            'content': 'This is test content'
        }
        
        output_path = formatter.save_note(note_data)
        
        assert output_path.exists()
        assert output_path.name == 'Test Note.md'
        
        content = output_path.read_text(encoding='utf-8')
        assert 'title: Test Note' in content
        assert 'This is test content' in content
    
    def test_save_note_with_metadata(self, temp_dir):
        """Test saving note with metadata"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Test Note',
            'content': 'Test content'
        }
        
        metadata = {
            'original_id': 'test-123',
            'tags': ['test'],
            'markdown': True
        }
        
        output_path = formatter.save_note(note_data, metadata)
        
        content = output_path.read_text(encoding='utf-8')
        assert 'original_id: test-123' in content
        assert 'tags:' in content
        assert '- test' in content
    
    def test_save_note_with_folder_organization(self, temp_dir):
        """Test saving note with folder organization (Phase 2)"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Project Note',
            'content': 'Project content'
        }
        
        metadata = {
            '_folder_path': 'Projects/Work',
            'tags': ['project']
        }
        
        output_path = formatter.save_note(note_data, metadata)
        
        assert output_path.parent.name == 'Work'
        assert output_path.parent.parent.name == 'Projects'
        assert output_path.name == 'Project Note.md'
    
    def test_save_note_filename_conflict(self, temp_dir):
        """Test handling filename conflicts"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Duplicate Note',
            'content': 'First note'
        }
        
        # Save first note
        first_path = formatter.save_note(note_data)
        assert first_path.name == 'Duplicate Note.md'
        
        # Save second note with same title
        note_data['content'] = 'Second note'
        second_path = formatter.save_note(note_data)
        assert second_path.name == 'Duplicate Note_1.md'
        
        # Save third note
        note_data['content'] = 'Third note'
        third_path = formatter.save_note(note_data)
        assert third_path.name == 'Duplicate Note_2.md'
    
    def test_save_all_notes(self, temp_dir, sample_notes_dir):
        """Test saving multiple notes"""
        formatter = ObsidianFormatter(temp_dir)
        
        notes = [
            {
                'filename': 'note1.txt',
                'title': 'First Note',
                'content': 'First content'
            },
            {
                'filename': 'note2.txt', 
                'title': 'Second Note',
                'content': 'Second content'
            }
        ]
        
        metadata_map = {
            'note1.txt': {
                'original_id': 'id-1',
                'tags': ['first']
            },
            'note2.txt': {
                'original_id': 'id-2',
                'tags': ['second']
            }
        }
        
        saved_files = formatter.save_all_notes(notes, metadata_map)
        
        assert len(saved_files) == 2
        assert 'note1.txt' in saved_files
        assert 'note2.txt' in saved_files
        
        # Check first file
        first_path = saved_files['note1.txt']
        assert first_path.exists()
        content = first_path.read_text(encoding='utf-8')
        assert 'title: First Note' in content
        assert 'original_id: id-1' in content
        
        # Check second file
        second_path = saved_files['note2.txt']
        assert second_path.exists()
        content = second_path.read_text(encoding='utf-8')
        assert 'title: Second Note' in content
        assert 'original_id: id-2' in content
    
    def test_save_all_notes_with_errors(self, temp_dir):
        """Test saving notes when some fail"""
        formatter = ObsidianFormatter(temp_dir)
        
        notes = [
            {
                'filename': 'good.txt',
                'title': 'Good Note',
                'content': 'Good content'
            },
            {
                'filename': 'bad.txt',
                'title': '',  # Empty title might cause issues
                'content': 'Bad content'
            }
        ]
        
        metadata_map = {}
        saved_files = formatter.save_all_notes(notes, metadata_map)
        
        # Should handle errors gracefully
        assert len(saved_files) >= 1  # At least the good note should save
        assert 'good.txt' in saved_files
    
    @pytest.mark.edge_case
    def test_format_note_empty_content(self, temp_dir):
        """Test formatting note with empty content"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Empty Note',
            'content': ''
        }
        
        formatted = formatter.format_note(note_data)
        
        assert 'title: Empty Note' in formatted
        assert formatted.endswith('---\n\n')  # Should end with empty content
    
    @pytest.mark.edge_case
    def test_format_note_special_yaml_chars(self, temp_dir):
        """Test formatting with special YAML characters in title"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Title: with "quotes" and other: special chars',
            'content': 'Content'
        }
        
        formatted = formatter.format_note(note_data)
        
        # YAML should handle special characters properly
        lines = formatted.split('\n')
        yaml_section = []
        in_yaml = False
        
        for line in lines:
            if line == '---' and not in_yaml:
                in_yaml = True
                continue
            elif line == '---' and in_yaml:
                break
            elif in_yaml:
                yaml_section.append(line)
        
        yaml_content = '\n'.join(yaml_section)
        parsed = yaml.safe_load(yaml_content)
        assert parsed['title'] == 'Title: with "quotes" and other: special chars'
    
    @pytest.mark.edge_case
    def test_save_note_very_long_filename(self, temp_dir):
        """Test saving note with very long title"""
        formatter = ObsidianFormatter(temp_dir)
        
        long_title = 'A' * 200  # Very long title
        note_data = {
            'title': long_title,
            'content': 'Content'
        }
        
        output_path = formatter.save_note(note_data)
        
        # Filename should be truncated but valid
        assert output_path.exists()
        assert len(output_path.stem) <= 100  # Stem is filename without extension
    
    @pytest.mark.edge_case 
    def test_save_note_unicode_title(self, temp_dir):
        """Test saving note with Unicode characters in title"""
        formatter = ObsidianFormatter(temp_dir)
        
        note_data = {
            'title': 'Café résumé naïve',
            'content': 'Unicode content: 中文 日本語 한국어'
        }
        
        output_path = formatter.save_note(note_data)
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert 'Café résumé naïve' in content
        assert '中文 日本語 한국어' in content