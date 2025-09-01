"""
Editor Pipeline Framework
Extensible system for content transformations and enhancements during import
"""

from typing import Dict, Any, List, Optional, Tuple
from pipelines import ContentProcessor, TagInjector, FolderOrganizer, ContentTransformer, NoteSplitter


class EditorPipeline:
    """Main pipeline that orchestrates content processing with conditional execution"""
    
    def __init__(self):
        self.processors: List[ContentProcessor] = []
    
    def add_processor(self, processor: ContentProcessor):
        """Add a processor to the pipeline"""
        self.processors.append(processor)
    
    def remove_processor(self, processor_name: str):
        """Remove a processor by name"""
        self.processors = [p for p in self.processors if p.name != processor_name]
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Process content through all processors in sequence with conditional execution
        
        Args:
            content: The note content
            metadata: Note metadata
            context: Processing context (filename, original_path, etc.)
            
        Returns:
            Tuple of (processed_content, processed_metadata)
        """
        current_content = content
        current_metadata = metadata.copy()
        
        for processor in self.processors:
            try:
                # Each processor decides whether to run based on current metadata/context
                current_content, current_metadata = processor.process(
                    current_content, current_metadata, context
                )
            except Exception as e:
                print(f"Warning: Processor {processor.name} failed: {e}")
                # Continue with other processors
                continue
        
        return current_content, current_metadata
    
    def get_default_pipeline(self) -> 'EditorPipeline':
        """Create a pipeline with default processors"""
        pipeline = EditorPipeline()
        pipeline.add_processor(TagInjector())
        pipeline.add_processor(FolderOrganizer())
        pipeline.add_processor(ContentTransformer())
        return pipeline
    
    def get_note_splitter(self) -> Optional[NoteSplitter]:
        """Get the NoteSplitter processor if it exists in the pipeline"""
        for processor in self.processors:
            if isinstance(processor, NoteSplitter):
                return processor
        return None