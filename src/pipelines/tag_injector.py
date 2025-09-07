"""
Tag Injector Processor
Adds tags based on content analysis and filename patterns
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base_processor import ContentProcessor


class TagInjector(ContentProcessor):
    """Processor that adds tags based on content analysis and filename patterns"""
    
    def __init__(self, tag_rules: Optional[Dict[str, List[str]]] = None, **kwargs):
        """
        Initialize with tag rules
        
        Args:
            tag_rules: Dict mapping patterns to tag lists
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(**kwargs)
        self.tag_rules = tag_rules or {}
    
    @property
    def name(self) -> str:
        return "tag_injector"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Add tags based on content and filename analysis"""
        if not self.should_process(metadata, context):
            return content, metadata
            
        new_tags = set(metadata.get('tags', []))
        
        # Analyze filename for patterns
        filename = context.get('filename', '')
        new_tags.update(self._extract_filename_tags(filename))
        
        # Analyze content for patterns
        new_tags.update(self._extract_content_tags(content))
        
        # Update metadata
        updated_metadata = metadata.copy()
        updated_metadata['tags'] = sorted(list(new_tags))
        
        return content, updated_metadata
    
    def _extract_filename_tags(self, filename: str) -> List[str]:
        """Extract tags based on filename patterns"""
        tags = []
        
        # Check for date patterns (journal entries)
        if re.search(r'\d{2}-\d{2}-\d{4}', filename):
            tags.append('journal')
            
        # Check for specific prefixes
        if filename.startswith('#'):
            tags.append('reference')
            
        # Apply filename-specific rules
        filename_lower = filename.lower()
        for pattern, pattern_tags in self.tag_rules.items():
            if re.search(pattern, filename_lower):
                tags.extend(pattern_tags)
                
        return tags
    
    def _extract_content_tags(self, content: str) -> List[str]:
        """Extract tags based on content analysis"""
        tags = []
        content_lower = content.lower()
        
        # Apply content-specific rules
        for pattern, pattern_tags in self.tag_rules.items():
            if re.search(pattern, content_lower):
                tags.extend(pattern_tags)
            
        # Check for list patterns (might be reference lists)
        lines = content.split('\n')
        list_lines = sum(1 for line in lines if line.strip().startswith(('- ', '* ', '+ ')) or 
                        re.match(r'^\s*\d+\.\s', line))
        if list_lines > 3:  # More than 3 list items
            tags.append('lists')
            
        return tags