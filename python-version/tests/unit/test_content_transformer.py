"""
Unit tests for ContentTransformer processor.
"""

import pytest
from typing import Dict, Any

from src.pipelines.content_transformer import ContentTransformer


class TestContentTransformer:
    """Test cases for ContentTransformer processor"""
    
    def test_init_default(self):
        """Test ContentTransformer initialization with defaults"""
        transformer = ContentTransformer()
        
        assert transformer.name == "content_transformer"
        assert isinstance(transformer.transformation_rules, dict)
        assert len(transformer.transformation_rules) > 0
    
    def test_init_with_custom_rules(self):
        """Test ContentTransformer initialization with custom rules"""
        custom_rules = {
            r'old_pattern': 'new_replacement',
            r'another_pattern': 'another_replacement'
        }
        
        transformer = ContentTransformer(transformation_rules=custom_rules)
        
        assert transformer.transformation_rules == custom_rules
        assert transformer.name == "content_transformer"
    
    def test_init_with_base_params(self):
        """Test ContentTransformer initialization with base class parameters"""
        transformer = ContentTransformer(
            enabled_tags=['work'],
            disabled_tags=['personal']
        )
        
        assert transformer.enabled_tags == ['work']
        assert transformer.disabled_tags == ['personal']
    
    def test_default_transformation_rules(self):
        """Test the default transformation rules"""
        transformer = ContentTransformer()
        rules = transformer._default_transformation_rules()
        
        # Check that we have expected patterns
        assert isinstance(rules, dict)
        assert len(rules) > 0
        
        # Test that keys are strings (regex patterns) and values are strings (replacements)
        for pattern, replacement in rules.items():
            assert isinstance(pattern, str)
            assert isinstance(replacement, str)
    
    def test_process_no_changes_needed(self):
        """Test processing when no transformations are needed"""
        transformer = ContentTransformer(transformation_rules={})
        
        content = "This is clean content\nWith proper formatting"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # Content should be cleaned but otherwise unchanged
        assert result_content == content
        assert result_metadata == metadata
    
    def test_process_custom_transformation_rules(self):
        """Test processing with custom transformation rules"""
        custom_rules = {
            r'old_word': 'new_word',
            r'pattern(\d+)': r'replacement\1'
        }
        
        transformer = ContentTransformer(transformation_rules=custom_rules)
        
        content = "This has old_word and pattern123 in it"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        assert "new_word" in result_content
        assert "replacement123" in result_content
        assert "old_word" not in result_content
        assert "pattern123" not in result_content
        assert result_metadata == metadata
    
    def test_process_should_not_process(self):
        """Test processing skipped when should_process returns False"""
        transformer = ContentTransformer(disabled_tags=['skip'])
        
        content = "Content with   extra    spaces   "
        metadata = {"tags": ["skip", "test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # Should return unchanged since processing was skipped
        assert result_content == content
        assert result_metadata == metadata
    
    def test_process_multiple_transformations(self):
        """Test processing applies multiple transformation rules"""
        custom_rules = {
            r'foo': 'bar',
            r'hello': 'hi',
            r'world': 'universe'
        }
        
        transformer = ContentTransformer(transformation_rules=custom_rules)
        
        content = "foo says hello world"
        metadata = {"tags": []}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        assert result_content == "bar says hi universe"
        assert result_metadata == metadata
    
    def test_clean_whitespace_trailing_spaces(self):
        """Test whitespace cleaning removes trailing spaces"""
        transformer = ContentTransformer()
        
        content = "Line with trailing spaces   \nAnother line  \nNormal line"
        expected = "Line with trailing spaces\nAnother line\nNormal line"
        
        result = transformer._clean_whitespace(content)
        
        assert result == expected
    
    def test_clean_whitespace_excessive_blank_lines(self):
        """Test whitespace cleaning removes excessive blank lines"""
        transformer = ContentTransformer()
        
        content = "First line\n\n\n\n\nSecond line\n\n\nThird line"
        
        result = transformer._clean_whitespace(content)
        
        # Should allow maximum 2 consecutive blank lines
        lines = result.split('\n')
        blank_count = 0
        max_consecutive_blanks = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
                max_consecutive_blanks = max(max_consecutive_blanks, blank_count)
            else:
                blank_count = 0
        
        assert max_consecutive_blanks <= 2
        assert "First line" in result
        assert "Second line" in result
        assert "Third line" in result
    
    def test_clean_whitespace_preserves_single_blank_lines(self):
        """Test whitespace cleaning preserves single blank lines"""
        transformer = ContentTransformer()
        
        content = "First paragraph\n\nSecond paragraph\n\nThird paragraph"
        
        result = transformer._clean_whitespace(content)
        
        assert result == content  # Should be unchanged
        assert result.count('\n\n') == 2  # Two single blank lines preserved
    
    def test_clean_whitespace_strips_leading_trailing(self):
        """Test whitespace cleaning strips leading and trailing whitespace"""
        transformer = ContentTransformer()
        
        content = "\n\n  Content in middle  \n\n"
        expected = "Content in middle"
        
        result = transformer._clean_whitespace(content)
        
        assert result == expected
    
    def test_clean_whitespace_empty_content(self):
        """Test whitespace cleaning with empty content"""
        transformer = ContentTransformer()
        
        result = transformer._clean_whitespace("")
        assert result == ""
        
        result = transformer._clean_whitespace("   \n\n  \n  ")
        assert result == ""
    
    def test_process_with_default_rules_multiple_newlines(self):
        """Test processing with default rules fixes multiple newlines"""
        transformer = ContentTransformer()
        
        content = "First paragraph\n\n\n\n\nSecond paragraph"
        metadata = {"tags": []}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # Should reduce excessive newlines
        assert result_content.count('\n\n\n') == 0
        assert "First paragraph" in result_content
        assert "Second paragraph" in result_content
        assert result_metadata == metadata
    
    def test_process_with_default_rules_header_spacing(self):
        """Test processing with default rules fixes header spacing"""
        transformer = ContentTransformer()
        
        content = "#Header\n##   Another Header   \n### Third Header"
        metadata = {"tags": []}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # Headers should be properly formatted
        assert "# Header\n" in result_content
        assert "# Another Header\n" in result_content
        assert "# Third Header" in result_content
        assert result_metadata == metadata
    
    def test_process_with_default_rules_list_formatting(self):
        """Test processing with default rules standardizes list formatting"""
        transformer = ContentTransformer()
        
        content = "  * Item one\n   + Item two\n    - Item three"
        metadata = {"tags": []}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # All lists should use standard format
        lines = result_content.split('\n')
        for line in lines:
            if line.strip():
                assert line.startswith('- ') or not any(line.strip().startswith(prefix) for prefix in ['*', '+', '-'])
        
        assert result_metadata == metadata
    
    def test_process_complex_content_transformation(self):
        """Test processing with complex content requiring multiple transformations"""
        transformer = ContentTransformer()
        
        content = """#  My Document Title  


This is a paragraph with   trailing spaces   


*   First list item
+   Second list item  
   -   Third list item


##Another Header Without Spacing


More content here.



"""
        
        metadata = {"tags": ["document"]}
        context = {"filename": "document.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # Check various transformations
        assert result_content.startswith("# My Document Title")
        assert "# Another Header Without Spacing" in result_content
        assert "- First list item" in result_content
        assert "- Second list item" in result_content
        assert "- Third list item" in result_content
        
        # No excessive whitespace
        assert result_content.count('\n\n\n\n') == 0
        assert not result_content.endswith('\n\n\n')
        
        assert result_metadata == metadata
    
    @pytest.mark.edge_case
    def test_process_empty_content(self):
        """Test processing empty content"""
        transformer = ContentTransformer()
        
        content = ""
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        assert result_content == ""
        assert result_metadata == metadata
    
    @pytest.mark.edge_case
    def test_process_whitespace_only_content(self):
        """Test processing content with only whitespace"""
        transformer = ContentTransformer()
        
        content = "   \n\n  \t  \n  "
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        assert result_content == ""
        assert result_metadata == metadata
    
    @pytest.mark.edge_case
    def test_process_single_line_content(self):
        """Test processing single line content"""
        transformer = ContentTransformer()
        
        content = "Just a single line with trailing spaces   "
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        assert result_content == "Just a single line with trailing spaces"
        assert result_metadata == metadata
    
    @pytest.mark.edge_case
    def test_process_regex_edge_cases(self):
        """Test processing with regex edge cases"""
        custom_rules = {
            r'\$(\d+)': r'USD \1',  # Dollar amounts
            r'([A-Z]+)\s+([A-Z]+)': r'\1_\2',  # Consecutive caps
        }
        
        transformer = ContentTransformer(transformation_rules=custom_rules)
        
        content = "I paid $50 for ABC XYZ widget"
        metadata = {"tags": []}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        assert "USD 50" in result_content
        assert "ABC_XYZ" in result_content
        assert result_metadata == metadata
    
    @pytest.mark.integration
    def test_process_realistic_note_content(self):
        """Integration test with realistic note content"""
        transformer = ContentTransformer()
        
        content = """#   My Recipe Notes   



## Ingredients

*  2 cups flour  
+  1 cup sugar   
   -  1/2 cup butter




## Instructions  

1. Mix ingredients
2. Bake at 350°F


##Notes




Remember to preheat oven!



"""
        
        metadata = {"tags": ["recipes", "cooking"]}
        context = {"filename": "recipe.txt"}
        
        result_content, result_metadata = transformer.process(content, metadata, context)
        
        # Check that content is properly formatted
        lines = result_content.split('\n')
        
        # Headers should be properly spaced
        assert any("# My Recipe Notes" in line for line in lines)
        assert any("# Ingredients" in line for line in lines)
        assert any("# Instructions" in line for line in lines)
        assert any("# Notes" in line for line in lines)
        
        # Lists should be standardized
        assert "- 2 cups flour" in result_content
        assert "- 1 cup sugar" in result_content
        assert "- 1/2 cup butter" in result_content
        
        # No excessive whitespace
        blank_line_groups = result_content.split('\n\n')
        for group in blank_line_groups:
            if group.strip() == '':
                # No more than one blank line group should be empty
                continue
        
        # Content should be cleaned up but preserved
        assert "Mix ingredients" in result_content
        assert "Bake at 350°F" in result_content
        assert "Remember to preheat oven!" in result_content
        
        assert result_metadata == metadata