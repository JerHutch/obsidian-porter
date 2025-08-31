"""
Editor Pipeline Framework
Extensible system for content transformations and enhancements during import
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import re
from pathlib import Path


class ContentProcessor(ABC):
    """Abstract base class for content processors"""
    
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


class TagInjector(ContentProcessor):
    """Processor that adds tags based on content analysis and filename patterns"""
    
    def __init__(self, tag_rules: Optional[Dict[str, List[str]]] = None):
        """
        Initialize with tag rules
        
        Args:
            tag_rules: Dict mapping patterns to tag lists
        """
        self.tag_rules = tag_rules or self._default_tag_rules()
    
    @property
    def name(self) -> str:
        return "tag_injector"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Add tags based on content and filename analysis"""
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
    
    def _default_tag_rules(self) -> Dict[str, List[str]]:
        """Default tagging rules based on common patterns"""
        return {
            # Gaming
            r'(?i)(elden ring|dark souls|bloodborne|sekiro)': ['gaming', 'souls-like'],
            r'(?i)(zelda|breath of the wild|tears of the kingdom)': ['gaming', 'zelda'],
            r'(?i)(monster hunter|mhw|mhr)': ['gaming', 'monster-hunter'],
            r'(?i)(hollow knight|metroidvania)': ['gaming', 'metroidvania'],
            r'(?i)(cyberpunk|witcher|rpg)': ['gaming', 'rpg'],
            r'(?i)(nintendo|xbox|playstation|ps4|ps5)': ['gaming'],
            
            # Food & Recipes
            r'(?i)(cocktail|drink|gin|whiskey|rum|vodka|tequila)': ['cocktails', 'drinks'],
            r'(?i)(recipe|cooking|ingredient|oven|bake)': ['recipes', 'cooking'],
            r'(?i)(ferment|kimchi|kombucha|kraut)': ['fermentation', 'recipes'],
            r'(?i)(taco|soup|noodle|meatball|chicken)': ['recipes', 'food'],
            r'(?i)(restaurant|dining|meal)': ['food', 'dining'],
            
            # Music
            r'(?i)(drum.*bass|dnb|jungle|breakbeat)': ['music', 'drum-and-bass'],
            r'(?i)(mix|dj|tracklist|essential mix)': ['music', 'mixes'],
            r'(?i)(vinyl|record|album)': ['music', 'vinyl'],
            r'(?i)(hardcore|rave|breaks)': ['music', 'electronic'],
            
            # Health & Fitness
            r'(?i)(blood pressure|health|doctor|medical)': ['health'],
            r'(?i)(exercise|workout|fitness|gym)': ['fitness'],
            
            # Technology
            r'(?i)(synology|server|port|network)': ['technology', 'networking'],
            r'(?i)(ai|coding|programming|python|javascript)': ['technology', 'programming'],
            r'(?i)(pc|computer|benchmark|install)': ['technology', 'hardware'],
            
            # Entertainment
            r'(?i)(movie|film|cinema|watch)': ['entertainment', 'movies'],
            r'(?i)(book|read|novel|comic)': ['entertainment', 'books'],
            r'(?i)(anime|manga)': ['entertainment', 'anime'],
            r'(?i)(board game|game night)': ['entertainment', 'board-games'],
            
            # Gardening
            r'(?i)(plant|garden|grow|seed|soil)': ['gardening'],
            r'(?i)(raised bed|compost|fertilizer)': ['gardening', 'outdoor'],
        }
    
    def _extract_filename_tags(self, filename: str) -> List[str]:
        """Extract tags based on filename patterns"""
        tags = []
        
        # Check for date patterns (journal entries)
        if re.match(r'\d{2}-\d{2}-\d{4}', filename):
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
        
        # Check for recipe indicators
        recipe_indicators = ['ingredient', 'tablespoon', 'teaspoon', 'cup', 'ounce', 'serving', 'bake', 'cook', 'mix']
        if any(indicator in content_lower for indicator in recipe_indicators):
            tags.append('recipes')
            
        # Check for list patterns (might be reference lists)
        lines = content.split('\n')
        list_lines = sum(1 for line in lines if line.strip().startswith(('- ', '* ', '+ ', '1. ', '2. ')))
        if list_lines > 3:  # More than 3 list items
            tags.append('lists')
            
        return tags


class FolderOrganizer(ContentProcessor):
    """Processor that determines folder organization based on tags and content"""
    
    def __init__(self, organization_rules: Optional[Dict[str, str]] = None):
        """
        Initialize with organization rules
        
        Args:
            organization_rules: Dict mapping tag patterns to folder names
        """
        self.organization_rules = organization_rules or self._default_organization_rules()
    
    @property
    def name(self) -> str:
        return "folder_organizer"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Determine folder organization based on tags and content"""
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


class ContentTransformer(ContentProcessor):
    """Processor for general content transformations"""
    
    def __init__(self, transformation_rules: Optional[Dict[str, str]] = None):
        """
        Initialize with transformation rules
        
        Args:
            transformation_rules: Dict mapping regex patterns to replacements
        """
        self.transformation_rules = transformation_rules or self._default_transformation_rules()
    
    @property
    def name(self) -> str:
        return "content_transformer"
    
    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Apply content transformations"""
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


class EditorPipeline:
    """Main pipeline that orchestrates content processing"""
    
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
        Process content through all processors in sequence
        
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