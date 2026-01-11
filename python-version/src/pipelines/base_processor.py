"""
Base Content Processor
Abstract base class for all pipeline processors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class ContentProcessor(ABC):
    """Abstract base class for content processors"""
    
    def __init__(self, enabled_tags: Optional[List[str]] = None, disabled_tags: Optional[List[str]] = None):
        """
        Initialize processor with optional tag-based filtering
        
        Args:
            enabled_tags: Only process notes with these tags (None = process all)
            disabled_tags: Skip notes with these tags (None = skip none)
        """
        self.enabled_tags = enabled_tags
        self.disabled_tags = disabled_tags or []
    
    @abstractmethod
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Process content and return modified content and metadata
        
        Args:
            content: The note content
            metadata: Note metadata
            context: Processing context (filename, tags, etc.)
            
        Returns:
            Tuple of (modified_content, modified_metadata)
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Processor name for logging and configuration"""
        pass
    
    def should_process(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if this processor should run based on tags and context
        
        Args:
            metadata: Note metadata (including tags)
            context: Processing context
            
        Returns:
            True if processor should run, False otherwise
        """
        note_tags = set(metadata.get('tags', []))
        
        # Skip if note has any disabled tags
        if self.disabled_tags and any(tag in note_tags for tag in self.disabled_tags):
            return False
        
        # If enabled_tags is specified, note must have at least one enabled tag
        if self.enabled_tags:
            return any(tag in note_tags for tag in self.enabled_tags)
        
        # If no tag restrictions, always process
        return True