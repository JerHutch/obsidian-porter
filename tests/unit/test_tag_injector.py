"""
Unit tests for TagInjector processor.
"""

import pytest
from typing import Dict, Any, List

from src.pipelines.tag_injector import TagInjector


class TestTagInjector:
    """Test cases for TagInjector processor"""
    
    def test_init_default(self):
        """Test TagInjector initialization with defaults"""
        injector = TagInjector()
        
        assert injector.name == "tag_injector"
        assert injector.tag_rules == {}
        assert injector.enabled_tags is None
        assert injector.disabled_tags == []
    
    def test_init_with_tag_rules(self):
        """Test TagInjector initialization with custom tag rules"""
        tag_rules = {
            'project': ['work', 'development'],
            'meeting': ['work', 'collaboration']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        assert injector.tag_rules == tag_rules
        assert injector.name == "tag_injector"
    
    def test_init_with_base_params(self):
        """Test TagInjector initialization with base class parameters"""
        injector = TagInjector(
            enabled_tags=['work'],
            disabled_tags=['personal']
        )
        
        assert injector.enabled_tags == ['work']
        assert injector.disabled_tags == ['personal']
    
    def test_process_no_changes(self):
        """Test processing when no tags should be added"""
        injector = TagInjector()
        
        content = "Simple note content"
        metadata = {"tags": ["existing"]}
        context = {"filename": "simple.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["tags"] == ["existing"]
    
    def test_process_adds_filename_tags(self):
        """Test processing adds tags based on filename patterns"""
        injector = TagInjector()
        
        content = "Content"
        metadata = {"tags": []}
        context = {"filename": "01-15-2024.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        assert "journal" in result_metadata["tags"]
    
    def test_process_adds_content_tags(self):
        """Test processing adds tags based on content patterns"""
        injector = TagInjector()
        
        content = """My List:
- Item one
- Item two
- Item three
- Item four
- Item five"""
        metadata = {"tags": []}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        assert "lists" in result_metadata["tags"]
    
    def test_process_custom_tag_rules(self):
        """Test processing with custom tag rules"""
        tag_rules = {
            'project.*meeting': ['work', 'collaboration'],
            'urgent|important': ['priority']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        content = "This is an urgent project meeting"
        metadata = {"tags": ["existing"]}
        context = {"filename": "project_meeting.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        tags = result_metadata["tags"]
        assert "existing" in tags
        assert "work" in tags
        assert "collaboration" in tags
        assert "priority" in tags
    
    def test_process_merges_existing_tags(self):
        """Test that existing tags are preserved and merged"""
        injector = TagInjector()
        
        content = "Meeting notes with list:\n- Point 1\n- Point 2\n- Point 3\n- Point 4"
        metadata = {"tags": ["existing", "work"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        tags = result_metadata["tags"]
        assert "existing" in tags
        assert "work" in tags
        assert "lists" in tags
        assert len(set(tags)) == len(tags)  # No duplicates
    
    def test_process_sorts_tags(self):
        """Test that tags are sorted in output"""
        tag_rules = {
            'test': ['zebra', 'alpha', 'beta']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        content = "This is a test"
        metadata = {"tags": ["work"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        tags = result_metadata["tags"]
        assert tags == sorted(tags)
    
    def test_process_should_not_process(self):
        """Test processing skipped when should_process returns False"""
        injector = TagInjector(disabled_tags=['skip'])
        
        content = "Content that would normally get tags:\n- Item 1\n- Item 2\n- Item 3\n- Item 4"
        metadata = {"tags": ["skip", "existing"]}
        context = {"filename": "01-15-2024.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        # Should return unchanged since processing was skipped
        assert result_content == content
        assert result_metadata == metadata
    
    def test_extract_filename_tags_date_patterns(self):
        """Test filename tag extraction for date patterns"""
        injector = TagInjector()
        
        # Valid date formats
        tags = injector._extract_filename_tags("01-15-2024.txt")
        assert "journal" in tags
        
        tags = injector._extract_filename_tags("12-31-2023_notes.txt")
        assert "journal" in tags
        
        # Invalid date formats
        tags = injector._extract_filename_tags("2024-01-15.txt")
        assert "journal" not in tags
        
        tags = injector._extract_filename_tags("1-5-24.txt")
        assert "journal" not in tags
    
    def test_extract_filename_tags_reference_prefix(self):
        """Test filename tag extraction for reference prefix"""
        injector = TagInjector()
        
        tags = injector._extract_filename_tags("#reference.txt")
        assert "reference" in tags
        
        tags = injector._extract_filename_tags("#API_docs.txt")
        assert "reference" in tags
        
        tags = injector._extract_filename_tags("reference.txt")
        assert "reference" not in tags
    
    def test_extract_filename_tags_custom_rules(self):
        """Test filename tag extraction with custom rules"""
        tag_rules = {
            'meeting': ['work', 'collaboration'],
            'project.*plan': ['planning', 'project']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        tags = injector._extract_filename_tags("team_meeting.txt")
        assert "work" in tags
        assert "collaboration" in tags
        
        tags = injector._extract_filename_tags("project_planning.txt")
        assert "planning" in tags
        assert "project" in tags
    
    def test_extract_filename_tags_case_insensitive(self):
        """Test filename tag extraction is case insensitive"""
        tag_rules = {
            'meeting': ['work']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        tags = injector._extract_filename_tags("MEETING.txt")
        assert "work" in tags
        
        tags = injector._extract_filename_tags("Meeting_Notes.txt")
        assert "work" in tags
    
    def test_extract_content_tags_list_detection(self):
        """Test content tag extraction for list detection"""
        injector = TagInjector()
        
        # Various list formats with enough items
        content_dash = """Items:
- Item 1
- Item 2
- Item 3
- Item 4"""
        tags = injector._extract_content_tags(content_dash)
        assert "lists" in tags
        
        content_star = """Items:
* Item 1
* Item 2
* Item 3
* Item 4"""
        tags = injector._extract_content_tags(content_star)
        assert "lists" in tags
        
        content_numbered = """Items:
1. Item 1
2. Item 2
3. Item 3
4. Item 4
5. Item 5"""
        tags = injector._extract_content_tags(content_numbered)
        assert "lists" in tags
        
        # Too few items - should not tag as lists
        content_short = """Items:
- Item 1
- Item 2"""
        tags = injector._extract_content_tags(content_short)
        assert "lists" not in tags
    
    def test_extract_content_tags_custom_rules(self):
        """Test content tag extraction with custom rules"""
        tag_rules = {
            'urgent|important': ['priority'],
            'project.*status': ['work', 'project'],
            'deadline': ['time-sensitive']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        content = "This is an urgent project status update with a deadline"
        tags = injector._extract_content_tags(content)
        
        assert "priority" in tags
        assert "work" in tags
        assert "project" in tags
        assert "time-sensitive" in tags
    
    def test_extract_content_tags_case_insensitive(self):
        """Test content tag extraction is case insensitive"""
        tag_rules = {
            'meeting': ['work']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        tags = injector._extract_content_tags("MEETING notes")
        assert "work" in tags
        
        tags = injector._extract_content_tags("Meeting NOTES")
        assert "work" in tags
    
    def test_extract_content_tags_overlapping_rules(self):
        """Test content tag extraction with overlapping rules"""
        tag_rules = {
            'project': ['work'],
            'project.*meeting': ['collaboration']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        content = "project meeting notes"
        tags = injector._extract_content_tags(content)
        
        assert "work" in tags
        assert "collaboration" in tags
    
    @pytest.mark.edge_case
    def test_process_empty_content(self):
        """Test processing empty content"""
        injector = TagInjector()
        
        content = ""
        metadata = {"tags": ["existing"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["tags"] == ["existing"]
    
    @pytest.mark.edge_case
    def test_process_no_tags_metadata(self):
        """Test processing when metadata has no tags key"""
        injector = TagInjector()
        
        content = "Content with lists:\n- Item 1\n- Item 2\n- Item 3\n- Item 4"
        metadata = {}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        assert "tags" in result_metadata
        assert "lists" in result_metadata["tags"]
    
    @pytest.mark.edge_case
    def test_process_empty_filename(self):
        """Test processing with empty filename in context"""
        injector = TagInjector()
        
        content = "Content"
        metadata = {"tags": []}
        context = {}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        # Should work without filename
        assert isinstance(result_metadata["tags"], list)
    
    @pytest.mark.edge_case
    def test_extract_filename_tags_empty_filename(self):
        """Test filename tag extraction with empty filename"""
        injector = TagInjector()
        
        tags = injector._extract_filename_tags("")
        assert tags == []
    
    @pytest.mark.edge_case  
    def test_extract_content_tags_empty_content(self):
        """Test content tag extraction with empty content"""
        injector = TagInjector()
        
        tags = injector._extract_content_tags("")
        assert tags == []
    
    @pytest.mark.integration
    def test_complex_processing_scenario(self):
        """Integration test with complex content and filename"""
        tag_rules = {
            'meeting': ['work', 'collaboration'],
            'project': ['development'],
            'deadline': ['urgent']
        }
        
        injector = TagInjector(tag_rules=tag_rules)
        
        content = """Project Meeting Notes - Q1 Planning
        
        Agenda:
        - Review project status
        - Discuss upcoming deadlines
        - Plan next sprint
        - Resource allocation
        
        Action items:
        1. Update project timeline
        2. Schedule follow-up meeting
        3. Review budget constraints"""
        
        metadata = {"tags": ["planning"]}
        context = {"filename": "#project_meeting_01-15-2024.txt"}
        
        result_content, result_metadata = injector.process(content, metadata, context)
        
        assert result_content == content
        tags = result_metadata["tags"]
        
        # Should have original tags
        assert "planning" in tags
        
        # Should have filename-based tags
        assert "reference" in tags  # from # prefix
        assert "journal" in tags     # from date pattern
        assert "work" in tags        # from 'meeting' rule
        assert "collaboration" in tags  # from 'meeting' rule
        assert "development" in tags # from 'project' rule
        
        # Should have content-based tags
        assert "lists" in tags       # from list detection
        assert "urgent" in tags      # from 'deadline' in content
        
        # Tags should be sorted and unique
        assert tags == sorted(set(tags))