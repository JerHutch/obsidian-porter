"""
Content Transformer Processor  
Applies general content transformations and cleanup
"""

import re
from typing import Dict, Any, Optional, Tuple
from .base_processor import ContentProcessor


class ContentTransformer(ContentProcessor):
    """Processor for general content transformations"""
    
    def __init__(self, transformation_rules: Optional[Dict[str, str]] = None, **kwargs):
        """
        Initialize with transformation rules
        
        Args:
            transformation_rules: Dict mapping regex patterns to replacements
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(**kwargs)
        self.transformation_rules = transformation_rules or self._default_transformation_rules()
    
    @property
    def name(self) -> str:
        return "content_transformer"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Apply content transformations"""
        if not self.should_process(metadata, context):
            return content, metadata
            
        transformed_content = content
        
        # Apply transformation rules
        for pattern, replacement in self.transformation_rules.items():
            transformed_content = re.sub(pattern, replacement, transformed_content)
        
        # Clean up extra whitespace
        transformed_content = self._clean_whitespace(transformed_content)
        
        return transformed_content, metadata
    
    def _default_transformation_rules(self) -> Dict[str, str]:
        """Default content transformation rules"""
        return {
            # Clean up multiple consecutive newlines
            r'\n\s*\n\s*\n+': '\n\n',
            
            # Fix common spacing issues around headers
            r'#+\s*([^\n]+)\s*\n': r'# \1\n\n',
            
            # Standardize list formatting
            r'^\s*[-*+]\s+': '- ',
            
            # Clean up trailing spaces on lines
            r' +\n': '\n',
        }
    
    def _clean_whitespace(self, content: str) -> str:
        """Clean up whitespace in content"""
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in content.split('\n')]
        
        # Remove excessive blank lines (more than 2 consecutive)
        cleaned_lines = []
        blank_count = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 2:  # Allow up to 2 blank lines
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()