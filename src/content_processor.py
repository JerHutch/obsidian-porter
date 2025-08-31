"""
Content Processor for SimpleNote .txt files
Handles reading and basic processing of note content
"""

from pathlib import Path
from typing import List, Optional, Dict, Any


class ContentProcessor:
    """Processes SimpleNote .txt files for content extraction"""
    
    def __init__(self, notes_directory: Path):
        self.notes_directory = Path(notes_directory)
        
    def get_txt_files(self) -> List[Path]:
        """Get all .txt files from the notes directory"""
        if not self.notes_directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.notes_directory}")
            
        return list(self.notes_directory.glob("*.txt"))
    
    def read_note_content(self, file_path: Path) -> Optional[str]:
        """
        Read content from a .txt file
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            Content as string, or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content.strip()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def extract_title(self, content: str) -> str:
        """
        Extract title from note content
        Uses first line, removing markdown header syntax if present
        """
        if not content.strip():
            return "Untitled"
            
        lines = content.strip().split('\n')
        first_line = lines[0].strip()
        
        # Remove markdown header syntax
        if first_line.startswith('#'):
            title = first_line.lstrip('# ').strip()
        else:
            title = first_line
            
        return title if title else "Untitled"
    
    def process_content(self, content: str) -> str:
        """
        Process note content for Phase 1 (basic conversion)
        In Phase 1, we just preserve content as-is
        
        Args:
            content: Raw note content
            
        Returns:
            Processed content
        """
        # Phase 1: Simple preservation with minimal cleanup
        return content.strip()
    
    def get_note_data(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get complete note data from a .txt file
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            Dictionary with note data or None if error
        """
        content = self.read_note_content(file_path)
        if content is None:
            return None
            
        return {
            'filename': file_path.name,
            'title': self.extract_title(content),
            'content': self.process_content(content),
            'original_path': file_path
        }
    
    def process_all_notes(self) -> List[Dict[str, Any]]:
        """
        Process all .txt files in the notes directory
        
        Returns:
            List of note data dictionaries
        """
        notes = []
        txt_files = self.get_txt_files()
        
        print(f"Found {len(txt_files)} .txt files")
        
        for file_path in txt_files:
            note_data = self.get_note_data(file_path)
            if note_data:
                notes.append(note_data)
            else:
                print(f"Skipping file due to error: {file_path}")
                
        return notes