"""
Content Processor for SimpleNote .txt files
Handles reading and basic processing of note content
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from .interfaces import FileSystemInterface, RealFileSystem


class ContentProcessor:
    """Processes SimpleNote .txt files for content extraction"""
    
    def __init__(self, notes_directory: Path, file_system: Optional[FileSystemInterface] = None):
        self.notes_directory = Path(notes_directory)
        self.file_system = file_system or RealFileSystem()
        
    def get_txt_files(self) -> List[Path]:
        """Get all .txt files from the notes directory"""
        if not self.file_system.exists(self.notes_directory):
            raise FileNotFoundError(f"Directory not found: {self.notes_directory}")
            
        return self.file_system.glob(self.notes_directory, "*.txt")
    
    def read_note_content(self, file_path: Path) -> Optional[str]:
        """
        Read content from a .txt file
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            Content as string, or None if error
        """
        try:
            content = self.file_system.read_text(file_path)
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