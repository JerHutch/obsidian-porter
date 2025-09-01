"""
SimpleNote to Obsidian Import Package
Phase 3 Implementation - Enhanced with Note Splitting and Advanced Processing
"""

__version__ = "3.0.0"
__author__ = "Claude Code"

from .simplenote_importer import SimpleNoteImporter
from .metadata_parser import MetadataParser  
from .content_processor import ContentProcessor as FileContentProcessor
from .obsidian_formatter import ObsidianFormatter
from .editor_pipeline import EditorPipeline
from .pipelines import ContentProcessor as PipelineContentProcessor, TagInjector, FolderOrganizer, ContentTransformer, NoteSplitter
from .config import ImportConfig, ConfigManager

__all__ = [
    'SimpleNoteImporter',
    'MetadataParser', 
    'FileContentProcessor',
    'ObsidianFormatter',
    'EditorPipeline',
    'PipelineContentProcessor',
    'TagInjector',
    'FolderOrganizer', 
    'ContentTransformer',
    'NoteSplitter',
    'ImportConfig',
    'ConfigManager'
]