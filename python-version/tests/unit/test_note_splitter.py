"""
Unit tests for NoteSplitter processor.
"""

import pytest
from typing import Dict, Any, List

from src.pipelines.note_splitter import NoteSplitter


class TestNoteSplitter:
    """Test cases for NoteSplitter processor"""
    
    def test_init_default(self):
        """Test NoteSplitter initialization with defaults"""
        splitter = NoteSplitter()
        
        assert splitter.name == "note_splitter"
        assert splitter.split_config == {}
        assert splitter.enable_splitting is False  # Disabled by default
        assert splitter.split_header_level == 2
        assert splitter.preserve_main_header is True
        assert splitter.split_notes == []
    
    def test_init_with_split_config(self):
        """Test NoteSplitter initialization with custom split config"""
        split_config = {
            'enable_note_splitting': True,
            'split_header_level': 1,
            'preserve_main_header': False
        }
        
        splitter = NoteSplitter(split_config=split_config)
        
        assert splitter.split_config == split_config
        assert splitter.enable_splitting is True
        assert splitter.split_header_level == 1
        assert splitter.preserve_main_header is False
        assert splitter.name == "note_splitter"
    
    def test_init_with_base_params(self):
        """Test NoteSplitter initialization with base class parameters"""
        splitter = NoteSplitter(
            enabled_tags=['work'],
            disabled_tags=['personal'],
            split_config={'enable_note_splitting': True}
        )
        
        assert splitter.enabled_tags == ['work']
        assert splitter.disabled_tags == ['personal']
        assert splitter.enable_splitting is True
    
    def test_process_splitting_disabled(self):
        """Test processing when splitting is disabled"""
        splitter = NoteSplitter()  # Default has splitting disabled
        
        content = """# Main Title

## Section 1
Content for section 1

## Section 2
Content for section 2"""
        
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should return unchanged since splitting is disabled
        assert result_content == content
        assert result_metadata == metadata
        assert splitter.split_notes == []
    
    def test_process_should_not_process(self):
        """Test processing skipped when should_process returns False"""
        splitter = NoteSplitter(
            split_config={'enable_note_splitting': True},
            disabled_tags=['skip']
        )
        
        content = """## Section 1
Content 1

## Section 2
Content 2"""
        
        metadata = {"tags": ["skip", "test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should return unchanged since processing was skipped
        assert result_content == content
        assert result_metadata == metadata
        assert splitter.split_notes == []
    
    def test_process_no_splits_found(self):
        """Test processing when no splits are found"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = "This is content without headers that would trigger splitting"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should return unchanged since no splits found
        assert result_content == content
        assert result_metadata == metadata
        assert splitter.split_notes == []
    
    def test_process_splits_at_level_2(self):
        """Test processing splits content at header level 2"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = """# Main Title

Some intro content

## Section 1
Content for section 1

## Section 2  
Content for section 2

## Section 3
Content for section 3"""
        
        metadata = {"tags": ["test"], "title": "Main Title"}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should return first split section
        expected_first_content = """# Main Title

Some intro content"""
        assert result_content.strip() == expected_first_content.strip()
        assert result_metadata["title"] == "Main Title"
        assert result_metadata["_split_from"] == "test.txt"
        assert result_metadata["_split_index"] == 0
        
        # Should have created split notes (1 intro + 3 sections)
        assert len(splitter.split_notes) == 4
    
    def test_process_splits_at_level_1(self):
        """Test processing splits content at header level 1"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'split_header_level': 1
        })
        
        content = """# Section 1
Content 1

# Section 2
Content 2"""
        
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should split at level 1 headers
        assert len(splitter.split_notes) == 2
        assert "# Section 1" in result_content
        assert "Content 1" in result_content
    
    def test_process_preserve_main_header_true(self):
        """Test processing with preserve_main_header=True"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'preserve_main_header': True
        })
        
        content = """# Main Title

## Section 1
Content 1

## Section 2
Content 2"""
        
        metadata = {"tags": ["test"], "title": "Main Title"}
        context = {"filename": "main.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        split_notes = splitter.split_notes
        assert len(split_notes) == 3  # Main title section + 2 subsections
        
        # First split should keep original filename and title
        first_split = split_notes[0]
        assert first_split['filename'] == "main.txt"
        assert first_split['metadata']['title'] == "Main Title"
        
        # Other splits should have new filenames based on headers
        second_split = split_notes[1]
        assert second_split['filename'] == "Section-1"
        assert second_split['metadata']['title'] == "Section 1"
    
    def test_process_preserve_main_header_false(self):
        """Test processing with preserve_main_header=False"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'preserve_main_header': False
        })
        
        content = """# Main Title

## Section 1
Content 1

## Section 2
Content 2"""
        
        metadata = {"tags": ["test"], "title": "Main Title"}
        context = {"filename": "main.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        split_notes = splitter.split_notes
        assert len(split_notes) == 3  # Main title section + 2 subsections
        
        # All splits should have new filenames based on headers
        first_split = split_notes[0]
        assert first_split['filename'] == "untitled"  # No header in first section
        assert first_split['metadata']['title'] == ""  # Empty title for headerless section
        
        second_split = split_notes[1]
        assert second_split['filename'] == "Section-1"
        assert second_split['metadata']['title'] == "Section 1"
    
    def test_split_by_headers_level_2(self):
        """Test _split_by_headers with level 2 headers"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'split_header_level': 2
        })
        
        content = """# Main Title
Intro content

## Section 1
Content 1

### Subsection 1.1
Sub content

## Section 2
Content 2"""
        
        sections = splitter._split_by_headers(content)
        
        assert len(sections) == 3
        assert sections[0][0] == ""  # First section has no header
        assert sections[1][0] == "## Section 1"
        assert sections[2][0] == "## Section 2"
        
        # Check content includes everything until next header
        assert "### Subsection 1.1" in sections[1][1]
        assert "Sub content" in sections[1][1]
    
    def test_split_by_headers_level_1(self):
        """Test _split_by_headers with level 1 headers"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'split_header_level': 1
        })
        
        content = """# Section 1
Content 1

## Subsection 1.1
Sub content

# Section 2
Content 2"""
        
        sections = splitter._split_by_headers(content)
        
        assert len(sections) == 2
        assert sections[0][0] == "# Section 1"
        assert sections[1][0] == "# Section 2"
        
        # Level 2 headers should be included in content
        assert "## Subsection 1.1" in sections[0][1]
    
    def test_split_by_headers_no_headers(self):
        """Test _split_by_headers with no matching headers"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'split_header_level': 2
        })
        
        content = """# Only level 1 header
Content without level 2 headers

### Only level 3 headers
More content"""
        
        sections = splitter._split_by_headers(content)
        
        assert len(sections) == 1
        assert sections[0][0] == ""  # No header at target level
        assert "# Only level 1 header" in sections[0][1]
    
    def test_sanitize_header_filename_basic(self):
        """Test header filename sanitization with basic headers"""
        splitter = NoteSplitter()
        
        # Basic header
        filename = splitter._sanitize_header_filename("## My Header")
        assert filename == "My-Header"
        
        # Header with special characters
        filename = splitter._sanitize_header_filename("## My<>Header:With/Special\\Chars")
        assert filename == "My-Header-With-Special-Chars"  # Consecutive dashes get collapsed to one
    
    def test_sanitize_header_filename_edge_cases(self):
        """Test header filename sanitization edge cases"""
        splitter = NoteSplitter()
        
        # Multiple spaces and dashes
        filename = splitter._sanitize_header_filename("## My   Header   With    Spaces")
        assert filename == "My-Header-With-Spaces"
        
        # Leading/trailing dashes
        filename = splitter._sanitize_header_filename("## -My Header-")
        assert filename == "My-Header"
        
        # Empty after sanitization
        filename = splitter._sanitize_header_filename("## <>:/\\|?*")
        assert filename == "untitled"
        
        # Only header symbols
        filename = splitter._sanitize_header_filename("###")
        assert filename == "untitled"
    
    def test_get_split_notes_empty(self):
        """Test get_split_notes when no splits have been processed"""
        splitter = NoteSplitter()
        
        split_notes = splitter.get_split_notes()
        
        assert split_notes == []
    
    def test_get_split_notes_after_processing(self):
        """Test get_split_notes after processing splits"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = """## Section 1
Content 1

## Section 2
Content 2"""
        
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        splitter.process(content, metadata, context)
        split_notes = splitter.get_split_notes()
        
        assert len(split_notes) == 2
        
        # Check structure of split notes
        for split_note in split_notes:
            assert 'filename' in split_note
            assert 'content' in split_note
            assert 'metadata' in split_note
            assert 'context' in split_note
            assert split_note['metadata']['_split_from'] == "test.txt"
            assert '_split_index' in split_note['metadata']
    
    def test_split_metadata_inheritance(self):
        """Test that split notes inherit metadata properly"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = """## Section 1
Content 1

## Section 2
Content 2"""
        
        metadata = {
            "tags": ["test", "work"],
            "created": "2024-01-01",
            "source": "simplenote",
            "custom_field": "value"
        }
        context = {"filename": "test.txt"}
        
        splitter.process(content, metadata, context)
        split_notes = splitter.get_split_notes()
        
        for i, split_note in enumerate(split_notes):
            split_metadata = split_note['metadata']
            
            # Should inherit all original metadata
            assert split_metadata["tags"] == ["test", "work"]
            assert split_metadata["created"] == "2024-01-01"
            assert split_metadata["source"] == "simplenote"
            assert split_metadata["custom_field"] == "value"
            
            # Should add split-specific metadata
            assert split_metadata["_split_from"] == "test.txt"
            assert split_metadata["_split_index"] == i
            assert "title" in split_metadata
    
    @pytest.mark.edge_case
    def test_process_empty_content(self):
        """Test processing empty content"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = ""
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata == metadata
        assert splitter.split_notes == []
    
    @pytest.mark.edge_case
    def test_process_single_header(self):
        """Test processing with only one header (no splits)"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = """## Only Section
This is the only content section"""
        
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should not split with only one section
        assert result_content == content
        assert result_metadata == metadata
        assert splitter.split_notes == []
    
    @pytest.mark.edge_case
    def test_process_headers_with_no_content(self):
        """Test processing headers with no content between them"""
        splitter = NoteSplitter(split_config={'enable_note_splitting': True})
        
        content = """## Section 1

## Section 2

## Section 3"""
        
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        # Should still create splits even with minimal content
        assert len(splitter.split_notes) == 3
        
        for split_note in splitter.split_notes:
            assert len(split_note['content']) > 0  # Should at least contain the header
    
    @pytest.mark.integration
    def test_complex_splitting_scenario(self):
        """Integration test with complex content structure"""
        splitter = NoteSplitter(split_config={
            'enable_note_splitting': True,
            'split_header_level': 2,
            'preserve_main_header': True
        })
        
        content = """# Project Documentation

This is the main project overview.

## Installation

Here's how to install:

1. Download the package
2. Run setup script

### Requirements

- Python 3.8+
- pip

## Configuration

Configuration details:

### Environment Variables

Set these variables:
- API_KEY
- DATABASE_URL

### Config File

Create config.yaml with:
```yaml
app:
  debug: true
```

## Usage

How to use the application:

1. Start the service
2. Make requests

### Examples

Here are some examples...

## Troubleshooting

Common issues and solutions."""
        
        metadata = {
            "tags": ["documentation", "project"],
            "title": "Project Documentation",
            "created": "2024-01-01"
        }
        context = {"filename": "project_docs.txt"}
        
        result_content, result_metadata = splitter.process(content, metadata, context)
        
        split_notes = splitter.split_notes
        
        # Should create splits for each ## header
        assert len(split_notes) == 5  # Overview, Installation, Configuration, Usage, Troubleshooting
        
        # Check first split (overview)
        first_split = split_notes[0]
        assert first_split['filename'] == "project_docs.txt"  # Preserved main header
        assert first_split['metadata']['title'] == "Project Documentation"
        assert "This is the main project overview" in first_split['content']
        
        # Check other splits
        expected_titles = ["Installation", "Configuration", "Usage", "Troubleshooting"]
        expected_filenames = ["Installation", "Configuration", "Usage", "Troubleshooting"]
        
        for i, expected_title in enumerate(expected_titles):
            split_note = split_notes[i + 1] if len(split_notes) > i + 1 else None
            if split_note:
                assert split_note['metadata']['title'] == expected_title
                assert split_note['filename'] == expected_filenames[i]
                
                # Should include subsections (### headers)
                if expected_title == "Installation":
                    assert "### Requirements" in split_note['content']
                elif expected_title == "Configuration":
                    assert "### Environment Variables" in split_note['content']
                    assert "### Config File" in split_note['content']
        
        # All splits should inherit original metadata
        for split_note in split_notes:
            assert split_note['metadata']['tags'] == ["documentation", "project"]
            assert split_note['metadata']['created'] == "2024-01-01"
            assert split_note['metadata']['_split_from'] == "project_docs.txt"