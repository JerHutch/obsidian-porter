"""
Metadata Parser for SimpleNote Export
Parses notes.json to extract metadata and create filename-to-metadata mapping
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any
from dateutil.parser import parse
from datetime import datetime


class MetadataParser:
    """Parses SimpleNote JSON export to extract metadata"""
    
    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.metadata_map = {}
        
    def parse(self) -> Dict[str, Dict[str, Any]]:
        """
        Parse notes.json and return filename-to-metadata mapping
        
        Returns:
            Dict mapping filenames to metadata dictionaries
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract activeNotes array
        notes = data.get('activeNotes', [])
        
        for note in notes:
            metadata = self._extract_metadata(note)
            filename = self._generate_filename(note.get('content', ''))
            if filename:
                self.metadata_map[filename] = metadata
                
        return self.metadata_map
    
    def _extract_metadata(self, note: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from a note object"""
        metadata = {
            'original_id': note.get('id', ''),
            'created': self._parse_timestamp(note.get('creationDate')),
            'modified': self._parse_timestamp(note.get('modificationDate')),
            'tags': note.get('tags', []),
            'markdown': note.get('markdown', False),
            'pinned': note.get('pinned', False),
            'source': 'simplenote'
        }
        
        return metadata
    
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        if not timestamp_str:
            return None
            
        try:
            return parse(timestamp_str)
        except Exception as e:
            print(f"Warning: Could not parse timestamp '{timestamp_str}': {e}")
            return None
    
    def _generate_filename(self, content: str) -> Optional[str]:
        """
        Generate filename from note content
        Uses first line as title, similar to SimpleNote's txt export
        """
        if not content.strip():
            return None
            
        lines = content.strip().split('\n')
        first_line = lines[0].strip()
        
        # Remove markdown header syntax if present
        if first_line.startswith('#'):
            first_line = first_line.lstrip('# ').strip()
            
        if not first_line:
            return None
            
        # Clean filename (remove invalid characters)
        filename = self._sanitize_filename(first_line)
        return f"{filename}.txt"
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use as filename"""
        # Replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
            
        # Limit length and strip whitespace
        title = title.strip()[:100]  # Reasonable filename length
        
        return title if title else 'untitled'
    
    def get_metadata_for_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific filename"""
        return self.metadata_map.get(filename)