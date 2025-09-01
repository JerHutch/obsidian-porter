"""
Note Splitter Processor
Splits notes into separate files based on headers
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base_processor import ContentProcessor


class NoteSplitter(ContentProcessor):
    """Processor that splits notes into separate files based on headers"""
    
    def __init__(self, split_config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize with note splitting configuration
        
        Args:
            split_config: Dict with splitting rules and options
            **kwargs: Additional arguments passed to base class (including tag filtering)
        """
        super().__init__(**kwargs)
        self.split_config = split_config or {}
        self.enable_splitting = self.split_config.get('enable_note_splitting', False)
        self.split_header_level = self.split_config.get('split_header_level', 2)  # Default to ##
        self.preserve_main_header = self.split_config.get('preserve_main_header', True)
        self.split_notes = []  # Store split notes for later processing
    
    @property
    def name(self) -> str:
        return "note_splitter"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Split note content based on headers
        
        Returns:
            Original content and metadata if splitting disabled or conditions not met,
            or first split section if splitting enabled and conditions met
        """
        if not self.enable_splitting or not self.should_process(metadata, context):
            return content, metadata
            
        # Split the note based on headers
        split_sections = self._split_by_headers(content)
        
        if len(split_sections) <= 1:
            # No splits found, return original content
            return content, metadata
        
        # Store split sections for later processing
        filename = context.get('filename', 'unknown')
        self.split_notes = []
        
        for i, (header, section_content) in enumerate(split_sections):
            # Create metadata for split note
            split_metadata = metadata.copy()
            
            if i == 0 and self.preserve_main_header:
                # Keep original filename for first section
                split_filename = filename
                split_title = metadata.get('title', header)
            else:
                # Create new filename based on header
                split_filename = self._sanitize_header_filename(header)
                split_title = header.strip('#').strip()
            
            split_metadata['title'] = split_title
            split_metadata['_split_from'] = filename
            split_metadata['_split_index'] = i
            
            self.split_notes.append({
                'filename': split_filename,
                'content': section_content,
                'metadata': split_metadata,
                'context': context.copy()
            })
        
        # Return the first split section as the "main" note
        if self.split_notes:
            first_split = self.split_notes[0]
            return first_split['content'], first_split['metadata']
        
        return content, metadata
    
    def _split_by_headers(self, content: str) -> List[Tuple[str, str]]:
        """Split content by markdown headers at the specified level"""
        lines = content.split('\n')
        sections = []
        current_section = []
        current_header = ""
        header_pattern = '#' * self.split_header_level + ' '
        
        for line in lines:
            # Check if this line is a header at our target level
            if line.startswith(header_pattern) and not line.startswith('#' * (self.split_header_level + 1)):
                # Save previous section if it exists
                if current_section:
                    sections.append((current_header, '\n'.join(current_section).strip()))
                
                # Start new section
                current_header = line
                current_section = [line]
            else:
                current_section.append(line)
        
        # Don't forget the last section
        if current_section:
            sections.append((current_header, '\n'.join(current_section).strip()))
        
        return sections
    
    def _sanitize_header_filename(self, header: str) -> str:
        """Convert header to a safe filename"""
        # Remove markdown header symbols
        clean_title = header.strip('#').strip()
        
        # Replace invalid filename characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in invalid_chars:
            clean_title = clean_title.replace(char, '-')
        
        # Replace multiple spaces/dashes with single dash
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        
        # Remove leading/trailing dashes
        clean_title = clean_title.strip('-')
        
        # Ensure it's not empty
        if not clean_title:
            clean_title = "untitled"
        
        return clean_title
    
    def get_split_notes(self) -> List[Dict[str, Any]]:
        """Get all split notes from the last processing"""
        return self.split_notes