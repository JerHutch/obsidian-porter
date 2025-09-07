"""
Unit tests for EditorPipeline class and pipeline orchestration.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, Tuple

from src.editor_pipeline import EditorPipeline
from src.pipelines.base_processor import ContentProcessor
from src.pipelines.tag_injector import TagInjector
from src.pipelines.folder_organizer import FolderOrganizer
from src.pipelines.content_transformer import ContentTransformer
from src.pipelines.note_splitter import NoteSplitter


class MockProcessor(ContentProcessor):
    """Mock processor for testing"""
    
    def __init__(self, processor_name: str, should_fail: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._name = processor_name
        self.should_fail = should_fail
        self.call_count = 0
        self.last_content = None
        self.last_metadata = None
        self.last_context = None
    
    @property
    def name(self) -> str:
        return self._name
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        self.call_count += 1
        self.last_content = content
        self.last_metadata = metadata
        self.last_context = context
        
        if self.should_fail:
            raise Exception(f"Mock processor {self._name} failed")
        
        # Mock transformation: add processor name to content and metadata
        new_content = content + f" [processed by {self._name}]"
        new_metadata = metadata.copy()
        new_metadata[f"processed_by_{self._name}"] = True
        
        return new_content, new_metadata


class TestEditorPipeline:
    """Test cases for EditorPipeline class"""
    
    def test_init(self):
        """Test EditorPipeline initialization"""
        pipeline = EditorPipeline()
        
        assert pipeline.processors == []
    
    def test_add_processor(self):
        """Test adding processors to pipeline"""
        pipeline = EditorPipeline()
        mock_processor = MockProcessor("test_processor")
        
        pipeline.add_processor(mock_processor)
        
        assert len(pipeline.processors) == 1
        assert pipeline.processors[0] == mock_processor
    
    def test_add_multiple_processors(self):
        """Test adding multiple processors maintains order"""
        pipeline = EditorPipeline()
        processor1 = MockProcessor("processor1")
        processor2 = MockProcessor("processor2")
        processor3 = MockProcessor("processor3")
        
        pipeline.add_processor(processor1)
        pipeline.add_processor(processor2)
        pipeline.add_processor(processor3)
        
        assert len(pipeline.processors) == 3
        assert pipeline.processors[0].name == "processor1"
        assert pipeline.processors[1].name == "processor2"
        assert pipeline.processors[2].name == "processor3"
    
    def test_remove_processor(self):
        """Test removing processor by name"""
        pipeline = EditorPipeline()
        processor1 = MockProcessor("processor1")
        processor2 = MockProcessor("processor2")
        processor3 = MockProcessor("processor3")
        
        pipeline.add_processor(processor1)
        pipeline.add_processor(processor2)
        pipeline.add_processor(processor3)
        
        pipeline.remove_processor("processor2")
        
        assert len(pipeline.processors) == 2
        assert pipeline.processors[0].name == "processor1"
        assert pipeline.processors[1].name == "processor3"
    
    def test_remove_nonexistent_processor(self):
        """Test removing processor that doesn't exist"""
        pipeline = EditorPipeline()
        processor1 = MockProcessor("processor1")
        
        pipeline.add_processor(processor1)
        pipeline.remove_processor("nonexistent")
        
        assert len(pipeline.processors) == 1
        assert pipeline.processors[0].name == "processor1"
    
    def test_process_empty_pipeline(self):
        """Test processing with no processors"""
        pipeline = EditorPipeline()
        
        content = "Test content"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        assert result_content == content
        assert result_metadata == metadata
    
    def test_process_single_processor(self):
        """Test processing with single processor"""
        pipeline = EditorPipeline()
        mock_processor = MockProcessor("test_processor")
        pipeline.add_processor(mock_processor)
        
        content = "Test content"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        assert mock_processor.call_count == 1
        assert mock_processor.last_content == content
        assert mock_processor.last_metadata == metadata
        assert mock_processor.last_context == context
        
        assert result_content == "Test content [processed by test_processor]"
        assert result_metadata["processed_by_test_processor"] is True
        assert result_metadata["tags"] == ["test"]  # Original metadata preserved
    
    def test_process_multiple_processors(self):
        """Test processing with multiple processors in sequence"""
        pipeline = EditorPipeline()
        processor1 = MockProcessor("processor1")
        processor2 = MockProcessor("processor2")
        
        pipeline.add_processor(processor1)
        pipeline.add_processor(processor2)
        
        content = "Test content"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        # Both processors should be called
        assert processor1.call_count == 1
        assert processor2.call_count == 1
        
        # Second processor should receive output from first
        assert processor2.last_content == "Test content [processed by processor1]"
        assert processor2.last_metadata["processed_by_processor1"] is True
        
        # Final result should have both transformations
        assert result_content == "Test content [processed by processor1] [processed by processor2]"
        assert result_metadata["processed_by_processor1"] is True
        assert result_metadata["processed_by_processor2"] is True
    
    def test_process_processor_failure(self, capsys):
        """Test processing continues when a processor fails"""
        pipeline = EditorPipeline()
        processor1 = MockProcessor("processor1")
        failing_processor = MockProcessor("failing_processor", should_fail=True)
        processor3 = MockProcessor("processor3")
        
        pipeline.add_processor(processor1)
        pipeline.add_processor(failing_processor)
        pipeline.add_processor(processor3)
        
        content = "Test content"
        metadata = {"tags": ["test"]}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning: Processor failing_processor failed" in captured.out
        
        # First and third processors should have run
        assert processor1.call_count == 1
        assert failing_processor.call_count == 1
        assert processor3.call_count == 1
        
        # Result should have transformations from working processors only
        assert result_content == "Test content [processed by processor1] [processed by processor3]"
        assert result_metadata["processed_by_processor1"] is True
        assert "processed_by_failing_processor" not in result_metadata
        assert result_metadata["processed_by_processor3"] is True
    
    def test_process_metadata_isolation(self):
        """Test that original metadata is not modified"""
        pipeline = EditorPipeline()
        mock_processor = MockProcessor("test_processor")
        pipeline.add_processor(mock_processor)
        
        content = "Test content"
        metadata = {"tags": ["test"], "original": True}
        context = {"filename": "test.txt"}
        
        original_metadata_copy = metadata.copy()
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        # Original metadata should not be modified
        assert metadata == original_metadata_copy
        
        # Result metadata should have modifications
        assert result_metadata != metadata
        assert result_metadata["processed_by_test_processor"] is True
        assert result_metadata["original"] is True  # Original keys preserved
    
    def test_get_default_pipeline(self):
        """Test creation of default pipeline"""
        pipeline = EditorPipeline()
        default_pipeline = pipeline.get_default_pipeline()
        
        assert len(default_pipeline.processors) == 3
        
        # Check processor types and order
        processors = default_pipeline.processors
        assert isinstance(processors[0], TagInjector)
        assert isinstance(processors[1], FolderOrganizer)
        assert isinstance(processors[2], ContentTransformer)
    
    def test_get_note_splitter_exists(self):
        """Test getting NoteSplitter when it exists"""
        pipeline = EditorPipeline()
        tag_injector = TagInjector()
        note_splitter = NoteSplitter()
        
        pipeline.add_processor(tag_injector)
        pipeline.add_processor(note_splitter)
        
        result = pipeline.get_note_splitter()
        
        assert result is note_splitter
        assert isinstance(result, NoteSplitter)
    
    def test_get_note_splitter_not_exists(self):
        """Test getting NoteSplitter when it doesn't exist"""
        pipeline = EditorPipeline()
        tag_injector = TagInjector()
        
        pipeline.add_processor(tag_injector)
        
        result = pipeline.get_note_splitter()
        
        assert result is None
    
    def test_get_note_splitter_multiple(self):
        """Test getting NoteSplitter returns first one when multiple exist"""
        pipeline = EditorPipeline()
        note_splitter1 = NoteSplitter()
        note_splitter2 = NoteSplitter()
        
        pipeline.add_processor(note_splitter1)
        pipeline.add_processor(note_splitter2)
        
        result = pipeline.get_note_splitter()
        
        assert result is note_splitter1  # Should return the first one
    
    @pytest.mark.integration
    def test_process_with_actual_processors(self):
        """Integration test with actual processor instances"""
        pipeline = EditorPipeline()
        
        # Add real processors with minimal configuration
        tag_injector = TagInjector()
        content_transformer = ContentTransformer()
        
        pipeline.add_processor(tag_injector)
        pipeline.add_processor(content_transformer)
        
        content = "Project Meeting Notes\n\n  This is about our development project.  \n\n"
        metadata = {"tags": []}
        context = {"filename": "meeting-notes.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        # Should have some processing (exact results depend on processor implementation)
        assert isinstance(result_content, str)
        assert isinstance(result_metadata, dict)
        assert "tags" in result_metadata
    
    @pytest.mark.edge_case
    def test_process_empty_content(self):
        """Test processing empty content"""
        pipeline = EditorPipeline()
        mock_processor = MockProcessor("test_processor")
        pipeline.add_processor(mock_processor)
        
        content = ""
        metadata = {"tags": []}
        context = {"filename": "empty.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        assert result_content == " [processed by test_processor]"
        assert mock_processor.call_count == 1
    
    @pytest.mark.edge_case
    def test_process_empty_metadata(self):
        """Test processing with empty metadata"""
        pipeline = EditorPipeline()
        mock_processor = MockProcessor("test_processor")
        pipeline.add_processor(mock_processor)
        
        content = "Test content"
        metadata = {}
        context = {"filename": "test.txt"}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        assert result_content == "Test content [processed by test_processor]"
        assert result_metadata["processed_by_test_processor"] is True
        assert mock_processor.call_count == 1
    
    @pytest.mark.edge_case
    def test_process_empty_context(self):
        """Test processing with empty context"""
        pipeline = EditorPipeline()
        mock_processor = MockProcessor("test_processor")
        pipeline.add_processor(mock_processor)
        
        content = "Test content"
        metadata = {"tags": ["test"]}
        context = {}
        
        result_content, result_metadata = pipeline.process(content, metadata, context)
        
        assert result_content == "Test content [processed by test_processor]"
        assert mock_processor.last_context == {}
        assert mock_processor.call_count == 1