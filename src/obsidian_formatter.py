"""
Obsidian Formatter
Formats notes for Obsidian with YAML frontmatter and proper markdown structure
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ObsidianFormatter:
    """Formats notes for Obsidian vault with YAML frontmatter"""
    
    def __init__(self, output_directory: Path):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
    def format_note(self, note_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a note with YAML frontmatter for Obsidian
        
        Args:
            note_data: Note content and basic info
            metadata: Optional metadata from JSON export
            
        Returns:
            Formatted note content with frontmatter
        """
        frontmatter = self._create_frontmatter(note_data, metadata)
        content = note_data.get('content', '')
        
        # Combine frontmatter and content
        formatted_note = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n{content}"
        
        return formatted_note
    
    def _create_frontmatter(self, note_data: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create YAML frontmatter dictionary"""
        frontmatter = {
            'title': note_data.get('title', 'Untitled'),
            'source': 'simplenote'
        }
        
        if metadata:
            # Add timestamps if available
            if metadata.get('created'):
                frontmatter['created'] = self._format_datetime(metadata['created'])
            if metadata.get('modified'):
                frontmatter['modified'] = self._format_datetime(metadata['modified'])
                
            # Add other metadata
            if metadata.get('original_id'):
                frontmatter['original_id'] = metadata['original_id']
            if metadata.get('tags'):
                frontmatter['tags'] = metadata['tags']
            if metadata.get('markdown'):
                frontmatter['markdown'] = metadata['markdown']
            if metadata.get('pinned'):
                frontmatter['pinned'] = metadata['pinned']
        else:
            # Default values when no metadata available
            frontmatter['tags'] = []
            
        return frontmatter
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for YAML frontmatter"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        return str(dt)
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use as Obsidian filename"""
        # Replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
            
        # Replace other problematic characters for Obsidian
        title = title.replace('[', '(').replace(']', ')')
        
        # Limit length and strip whitespace
        title = title.strip()[:100]
        
        return title if title else 'untitled'
    
    def generate_filename(self, note_data: Dict[str, Any]) -> str:
        """
        Generate Obsidian-compatible filename
        
        Args:
            note_data: Note data with title
            
        Returns:
            Sanitized filename with .md extension
        """
        title = note_data.get('title', 'Untitled')
        safe_title = self._sanitize_filename(title)
        return f"{safe_title}.md"
    
    def save_note(self, note_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Format and save a note to the output directory
        
        Args:
            note_data: Note content and info
            metadata: Optional metadata
            
        Returns:
            Path to the saved file
        """
        formatted_content = self.format_note(note_data, metadata)
        filename = self.generate_filename(note_data)
        
        # Handle filename conflicts
        output_path = self.output_directory / filename
        counter = 1
        while output_path.exists():
            name_part = filename.rsplit('.md', 1)[0]
            output_path = self.output_directory / f"{name_part}_{counter}.md"
            counter += 1
            
        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
            
        return output_path
    
    def save_all_notes(self, notes: list, metadata_map: Dict[str, Dict[str, Any]]) -> Dict[str, Path]:
        """
        Save all notes to the output directory
        
        Args:
            notes: List of note data dictionaries
            metadata_map: Mapping of filenames to metadata
            
        Returns:
            Dictionary mapping original filenames to output paths
        """
        saved_files = {}
        
        print(f"Saving {len(notes)} notes to {self.output_directory}")
        
        for note_data in notes:
            original_filename = note_data.get('filename', '')
            metadata = metadata_map.get(original_filename)
            
            try:
                output_path = self.save_note(note_data, metadata)
                saved_files[original_filename] = output_path
                print(f"Saved: {original_filename} -> {output_path.name}")
            except Exception as e:
                print(f"Error saving {original_filename}: {e}")
                
        return saved_files