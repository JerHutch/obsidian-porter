"""
Unit tests for FolderOrganizer processor.
"""

import pytest
from typing import Dict, Any, List

from src.pipelines.folder_organizer import FolderOrganizer


class TestFolderOrganizer:
    """Test cases for FolderOrganizer processor"""
    
    def test_init_default(self):
        """Test FolderOrganizer initialization with defaults"""
        organizer = FolderOrganizer()
        
        assert organizer.name == "folder_organizer"
        assert isinstance(organizer.organization_rules, dict)
        assert len(organizer.organization_rules) > 0
        
        # Check some default rules exist
        assert 'cocktails' in organizer.organization_rules
        assert 'programming' in organizer.organization_rules
        assert 'journal' in organizer.organization_rules
    
    def test_init_with_custom_rules(self):
        """Test FolderOrganizer initialization with custom rules"""
        custom_rules = {
            'work': 'work',
            'personal': 'personal',
            'project': 'work/projects'
        }
        
        organizer = FolderOrganizer(organization_rules=custom_rules)
        
        assert organizer.organization_rules == custom_rules
        assert organizer.name == "folder_organizer"
    
    def test_init_with_base_params(self):
        """Test FolderOrganizer initialization with base class parameters"""
        organizer = FolderOrganizer(
            enabled_tags=['work'],
            disabled_tags=['personal']
        )
        
        assert organizer.enabled_tags == ['work']
        assert organizer.disabled_tags == ['personal']
    
    def test_default_organization_rules(self):
        """Test the default organization rules"""
        organizer = FolderOrganizer()
        rules = organizer._default_organization_rules()
        
        # Test specific mappings
        assert rules['cocktails'] == 'cocktails'
        assert rules['recipes'] == 'recipes'
        assert rules['fermentation'] == 'recipes/fermentation'
        assert rules['programming'] == 'tech/programming'
        assert rules['movies'] == 'entertainment/movies'
        assert rules['lists'] == 'reference/lists'
        assert rules['journal'] == 'journal'
        
        # Test that all values are strings
        for folder in rules.values():
            assert isinstance(folder, str)
            assert len(folder) > 0
    
    def test_process_tag_based_organization(self):
        """Test processing with tag-based folder organization"""
        organizer = FolderOrganizer()
        
        content = "Recipe content"
        metadata = {"tags": ["recipes", "cooking"]}
        context = {"filename": "recipe.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "recipes"  # First matching tag
        assert result_metadata["tags"] == ["recipes", "cooking"]  # Original tags preserved
    
    def test_process_hierarchical_folder(self):
        """Test processing with hierarchical folder assignment"""
        organizer = FolderOrganizer()
        
        content = "Programming notes"
        metadata = {"tags": ["programming", "technology"]}
        context = {"filename": "code.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "tech/programming"
    
    def test_process_journal_filename(self):
        """Test processing with journal filename pattern"""
        organizer = FolderOrganizer()
        
        content = "Daily journal entry"
        metadata = {"tags": []}
        context = {"filename": "01-15-2024.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "journal"
    
    def test_process_reference_filename(self):
        """Test processing with reference filename pattern"""
        organizer = FolderOrganizer()
        
        content = "Reference information"
        metadata = {"tags": []}
        context = {"filename": "#reference_doc.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "reference"
    
    def test_process_default_folder(self):
        """Test processing falls back to default folder"""
        organizer = FolderOrganizer()
        
        content = "Random content"
        metadata = {"tags": ["unknown-tag"]}
        context = {"filename": "random.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "misc"
    
    def test_process_tag_priority_over_filename(self):
        """Test that tag-based organization takes priority over filename patterns"""
        organizer = FolderOrganizer()
        
        content = "Recipe with date in filename"
        metadata = {"tags": ["recipes"]}
        context = {"filename": "01-15-2024_recipe.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "recipes"  # Tag wins over date pattern
    
    def test_process_should_not_process(self):
        """Test processing skipped when should_process returns False"""
        organizer = FolderOrganizer(disabled_tags=['skip'])
        
        content = "Content"
        metadata = {"tags": ["recipes", "skip"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        # Should return unchanged since processing was skipped
        assert result_content == content
        assert result_metadata == metadata
        assert "_folder_path" not in result_metadata
    
    def test_process_custom_organization_rules(self):
        """Test processing with custom organization rules"""
        custom_rules = {
            'work': 'work',
            'project': 'work/projects',
            'meeting': 'work/meetings'
        }
        
        organizer = FolderOrganizer(organization_rules=custom_rules)
        
        content = "Project content"
        metadata = {"tags": ["project", "work"]}
        context = {"filename": "project.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "work/projects"  # First matching tag
    
    def test_determine_folder_tag_matching(self):
        """Test _determine_folder with tag matching"""
        organizer = FolderOrganizer()
        
        # Single matching tag
        folder = organizer._determine_folder(["recipes"], "content", "file.txt")
        assert folder == "recipes"
        
        # Multiple matching tags - should return first match
        folder = organizer._determine_folder(["recipes", "cocktails"], "content", "file.txt")
        assert folder == "recipes"
        
        # Mixed matching and non-matching tags
        folder = organizer._determine_folder(["unknown", "recipes", "other"], "content", "file.txt")
        assert folder == "recipes"
    
    def test_determine_folder_filename_patterns(self):
        """Test _determine_folder with filename patterns"""
        organizer = FolderOrganizer()
        
        # Date pattern
        folder = organizer._determine_folder([], "content", "01-15-2024.txt")
        assert folder == "journal"
        
        folder = organizer._determine_folder([], "content", "12-31-2023_notes.txt")
        assert folder == "journal"
        
        # Reference pattern
        folder = organizer._determine_folder([], "content", "#reference.txt")
        assert folder == "reference"
        
        folder = organizer._determine_folder([], "content", "#API_docs.txt")
        assert folder == "reference"
    
    def test_determine_folder_invalid_date_patterns(self):
        """Test _determine_folder with invalid date patterns"""
        organizer = FolderOrganizer()
        
        # Invalid date formats should fall back to misc
        folder = organizer._determine_folder([], "content", "2024-01-15.txt")
        assert folder == "misc"
        
        folder = organizer._determine_folder([], "content", "1-5-24.txt")
        assert folder == "misc"
        
        folder = organizer._determine_folder([], "content", "January-15-2024.txt")
        assert folder == "misc"
    
    def test_determine_folder_no_matches(self):
        """Test _determine_folder with no matching patterns"""
        organizer = FolderOrganizer()
        
        folder = organizer._determine_folder([], "content", "random.txt")
        assert folder == "misc"
        
        folder = organizer._determine_folder(["unknown", "nonexistent"], "content", "file.txt")
        assert folder == "misc"
    
    def test_determine_folder_empty_inputs(self):
        """Test _determine_folder with empty inputs"""
        organizer = FolderOrganizer()
        
        folder = organizer._determine_folder([], "", "")
        assert folder == "misc"
        
        folder = organizer._determine_folder([], "content", "")
        assert folder == "misc"
    
    @pytest.mark.edge_case
    def test_process_no_tags(self):
        """Test processing when metadata has no tags"""
        organizer = FolderOrganizer()
        
        content = "Content"
        metadata = {}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "misc"
    
    @pytest.mark.edge_case
    def test_process_empty_context(self):
        """Test processing with empty context"""
        organizer = FolderOrganizer()
        
        content = "Content"
        metadata = {"tags": ["recipes"]}
        context = {}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata["_folder_path"] == "recipes"
    
    @pytest.mark.edge_case
    def test_process_metadata_isolation(self):
        """Test that original metadata is not modified"""
        organizer = FolderOrganizer()
        
        content = "Content"
        metadata = {"tags": ["recipes"], "other": "data"}
        context = {"filename": "test.txt"}
        
        original_metadata = metadata.copy()
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        # Original metadata should be unchanged
        assert metadata == original_metadata
        
        # Result metadata should have folder path added
        assert result_metadata != metadata
        assert result_metadata["_folder_path"] == "recipes"
        assert result_metadata["tags"] == ["recipes"]
        assert result_metadata["other"] == "data"
    
    @pytest.mark.integration
    def test_complex_organization_scenario(self):
        """Integration test with complex tag and filename scenarios"""
        custom_rules = {
            'work': 'work',
            'project': 'work/projects',
            'meeting': 'work/meetings',
            'personal': 'personal',
            'recipes': 'cooking/recipes',
            'health': 'personal/health'
        }
        
        organizer = FolderOrganizer(organization_rules=custom_rules)
        
        test_cases = [
            # (tags, filename, expected_folder)
            (["work", "meeting"], "team_meeting.txt", "work"),
            (["project", "work"], "project_plan.txt", "work/projects"),
            (["personal", "health"], "workout.txt", "personal"),
            (["health", "personal"], "diet.txt", "personal/health"),
            ([], "01-15-2024.txt", "journal"),
            ([], "#reference.txt", "reference"),
            (["unknown"], "random.txt", "misc"),
            ([], "normal_file.txt", "misc")
        ]
        
        for tags, filename, expected_folder in test_cases:
            content = f"Content for {filename}"
            metadata = {"tags": tags}
            context = {"filename": filename}
            
            result_content, result_metadata = organizer.process(content, metadata, context)
            
            assert result_content == content
            assert result_metadata["_folder_path"] == expected_folder, \
                f"Failed for tags={tags}, filename={filename}. Expected {expected_folder}, got {result_metadata['_folder_path']}"
    
    def test_folder_path_metadata_key(self):
        """Test that folder path is stored in the correct metadata key"""
        organizer = FolderOrganizer()
        
        content = "Content"
        metadata = {"tags": ["recipes"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = organizer.process(content, metadata, context)
        
        # Should use _folder_path key (with underscore prefix to indicate internal use)
        assert "_folder_path" in result_metadata
        assert result_metadata["_folder_path"] == "recipes"
        
        # Should not create other folder-related keys
        folder_keys = [key for key in result_metadata.keys() if 'folder' in key.lower()]
        assert len(folder_keys) == 1
        assert folder_keys[0] == "_folder_path"