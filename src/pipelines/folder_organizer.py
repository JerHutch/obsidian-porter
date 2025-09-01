"""
Folder Organizer Processor
Determines folder organization based on tags and content
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base_processor import ContentProcessor


class FolderOrganizer(ContentProcessor):
    """Processor that determines folder organization based on tags and content"""
    
    def __init__(self, organization_rules: Optional[Dict[str, str]] = None, **kwargs):
        """
        Initialize with organization rules
        
        Args:
            organization_rules: Dict mapping tag patterns to folder names
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(**kwargs)
        self.organization_rules = organization_rules or self._default_organization_rules()
    
    @property
    def name(self) -> str:
        return "folder_organizer"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Determine folder organization based on tags and content"""
        if not self.should_process(metadata, context):
            return content, metadata
            
        tags = metadata.get('tags', [])
        
        # Determine folder based on tags
        folder_path = self._determine_folder(tags, content, context.get('filename', ''))
        
        # Add folder info to context for the formatter
        updated_metadata = metadata.copy()
        updated_metadata['_folder_path'] = folder_path
        
        return content, updated_metadata
    
    def _default_organization_rules(self) -> Dict[str, str]:
        """Default folder organization rules"""
        return {
            'cocktails': 'cocktails',
            'drinks': 'cocktails',
            'recipes': 'recipes',
            'cooking': 'recipes',
            'fermentation': 'recipes/fermentation',
            'gaming': 'gaming',
            'music': 'music',
            'drum-and-bass': 'music/electronic',
            'electronic': 'music/electronic',
            'mixes': 'music/mixes',
            'vinyl': 'music/vinyl',
            'health': 'health',
            'fitness': 'health',
            'technology': 'tech',
            'programming': 'tech/programming',
            'networking': 'tech/networking',
            'hardware': 'tech/hardware',
            'entertainment': 'entertainment',
            'movies': 'entertainment/movies',
            'books': 'entertainment/books',
            'anime': 'entertainment/anime',
            'board-games': 'entertainment/games',
            'gardening': 'gardening',
            'journal': 'journal',
            'lists': 'reference/lists',
            'reference': 'reference',
        }
    
    def _determine_folder(self, tags: List[str], content: str, filename: str) -> str:
        """Determine the appropriate folder based on tags, content, and filename"""
        # Check for specific folder mappings based on tags
        for tag in tags:
            if tag in self.organization_rules:
                return self.organization_rules[tag]
        
        # Check for journal entries (date-based filenames)
        if re.match(r'\d{2}-\d{2}-\d{4}', filename):
            return 'journal'
            
        # Check for reference notes (starting with #)
        if filename.startswith('#'):
            return 'reference'
            
        # Default to root or 'misc'
        return 'misc'