"""
SimpleNote to Obsidian Import Package
Phase 2 Implementation - Enhanced with Editor Pipeline and Configuration
"""

__version__ = "2.0.0"
__author__ = "Claude Code"

from .simplenote_importer import SimpleNoteImporter
from .metadata_parser import MetadataParser  
from .content_processor import ContentProcessor
from .obsidian_formatter import ObsidianFormatter
from .editor_pipeline import EditorPipeline, TagInjector, FolderOrganizer, ContentTransformer
from .config import ImportConfig, ConfigManager

__all__ = [
    'SimpleNoteImporter',
    'MetadataParser', 
    'ContentProcessor',
    'ObsidianFormatter',
    'EditorPipeline',
    'TagInjector',
    'FolderOrganizer', 
    'ContentTransformer',
    'ImportConfig',
    'ConfigManager'
]