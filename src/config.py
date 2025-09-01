"""
Configuration System for SimpleNote Importer
Handles Phase 2 settings and options
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import json


@dataclass
class ImportConfig:
    """Configuration for the import process"""
    
    # Phase 2 Features
    enable_editor_pipeline: bool = True
    enable_auto_tagging: bool = True
    enable_folder_organization: bool = True
    enable_content_transformation: bool = True
    
    # Phase 3 Features
    enable_note_splitting: bool = False
    
    # Organization Settings
    organize_by_folder: bool = True
    folder_structure: str = "tags"  # "tags", "date", "custom", "flat"
    create_index_files: bool = False
    
    # Tagging Settings
    auto_tag_rules: Dict[str, List[str]] = field(default_factory=dict)
    tag_blacklist: List[str] = field(default_factory=list)
    tag_whitelist: Optional[List[str]] = None
    
    # Content Processing
    clean_whitespace: bool = True
    standardize_headers: bool = True
    fix_list_formatting: bool = True
    
    # Output Settings
    output_format: str = "obsidian"  # "obsidian", "standard"
    preserve_original_structure: bool = False
    create_backlinks: bool = False
    
    # Custom Rules
    custom_tag_rules: Dict[str, List[str]] = field(default_factory=dict)
    custom_folder_rules: Dict[str, str] = field(default_factory=dict)
    custom_transformations: Dict[str, str] = field(default_factory=dict)
    
    # Note Splitting Settings
    split_header_level: int = 2  # Split on ## headers by default
    preserve_main_header: bool = True  # Keep original file with first section
    split_notes_patterns: List[str] = field(default_factory=list)  # Only split notes matching these patterns
    split_enabled_tags: List[str] = field(default_factory=lambda: ['cocktails', 'recipes', 'drinks'])  # Only split notes with these tags
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'ImportConfig':
        """Load configuration from YAML or JSON file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            return cls()  # Return default config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:  # Assume YAML
                    data = yaml.safe_load(f)
            
            return cls(**data)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return cls()  # Return default config on error
    
    def save_to_file(self, config_path: Path):
        """Save configuration to YAML file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict, excluding private fields
        config_dict = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                config_dict[key] = value
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {config_path}: {e}")
    
    def get_phase2_preset(self, preset_name: str) -> 'ImportConfig':
        """Get a pre-configured setup for common use cases"""
        presets = {
            'minimal': ImportConfig(
                enable_editor_pipeline=False,
                enable_auto_tagging=False,
                enable_folder_organization=False,
                enable_content_transformation=False,
                organize_by_folder=False
            ),
            
            'basic': ImportConfig(
                enable_editor_pipeline=True,
                enable_auto_tagging=True,
                enable_folder_organization=False,
                enable_content_transformation=True,
                organize_by_folder=False
            ),
            
            'organized': ImportConfig(
                enable_editor_pipeline=True,
                enable_auto_tagging=True,
                enable_folder_organization=True,
                enable_content_transformation=True,
                organize_by_folder=True,
                folder_structure="tags",
                create_index_files=False
            ),
            
            'full': ImportConfig(
                enable_editor_pipeline=True,
                enable_auto_tagging=True,
                enable_folder_organization=True,
                enable_content_transformation=True,
                organize_by_folder=True,
                folder_structure="tags",
                create_index_files=True,
                create_backlinks=True
            ),
            
            'phase3': ImportConfig(
                enable_editor_pipeline=True,
                enable_auto_tagging=True,
                enable_folder_organization=True,
                enable_content_transformation=True,
                enable_note_splitting=True,
                organize_by_folder=True,
                folder_structure="tags",
                split_header_level=2,
                preserve_main_header=True
            )
        }
        
        return presets.get(preset_name, ImportConfig())


class ConfigManager:
    """Manager for handling configuration operations"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default config file
        self.default_config_file = self.config_dir / "import_config.yaml"
    
    def load_config(self, config_file: Optional[Path] = None) -> ImportConfig:
        """Load configuration from file or return default"""
        config_file = config_file or self.default_config_file
        return ImportConfig.load_from_file(config_file)
    
    def save_config(self, config: ImportConfig, config_file: Optional[Path] = None):
        """Save configuration to file"""
        config_file = config_file or self.default_config_file
        config.save_to_file(config_file)
    
    def create_sample_config(self, config_file: Optional[Path] = None):
        """Create a sample configuration file with documentation"""
        config_file = config_file or self.config_dir / "sample_config.yaml"
        
        sample_config = {
            '# SimpleNote Importer Configuration': None,
            '# Phase 2 Features': None,
            'enable_editor_pipeline': True,
            'enable_auto_tagging': True,
            'enable_folder_organization': True,
            'enable_content_transformation': True,
            
            '# Organization Settings': None,
            'organize_by_folder': True,
            'folder_structure': 'tags',  # options: tags, date, custom, flat
            'create_index_files': False,
            
            '# Auto-tagging Rules (regex patterns -> tags)': None,
            'custom_tag_rules': {
                'cocktail|drink|recipe': ['recipes', 'drinks'],
                'gaming|game|play': ['gaming'],
                'music|song|album': ['music']
            },
            
            '# Folder Organization Rules (tag -> folder)': None,
            'custom_folder_rules': {
                'recipes': 'cooking',
                'gaming': 'entertainment/games',
                'music': 'media/music'
            },
            
            '# Content Processing': None,
            'clean_whitespace': True,
            'standardize_headers': True,
            'fix_list_formatting': True,
            
            '# Phase 3 Features - Note Splitting': None,
            'enable_note_splitting': False,
            'split_header_level': 2,  # Split on ## headers
            'preserve_main_header': True,
            'split_notes_patterns': [],  # Only split notes matching these patterns (empty = all)
            'split_enabled_tags': ['cocktails', 'recipes', 'drinks'],  # Only split notes with these tags
            
            '# Output Settings': None,
            'output_format': 'obsidian',
            'preserve_original_structure': False,
            'create_backlinks': False
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                for key, value in sample_config.items():
                    if value is None:  # Comment line
                        f.write(f"{key}\n")
                    else:
                        yaml.dump({key: value}, f, default_flow_style=False, indent=2)
                        
            print(f"Sample configuration created: {config_file}")
        except Exception as e:
            print(f"Error creating sample config: {e}")
    
    def validate_config(self, config: ImportConfig) -> List[str]:
        """Validate configuration and return list of warnings/errors"""
        warnings = []
        
        # Validate folder structure option
        valid_structures = ['tags', 'date', 'custom', 'flat']
        if config.folder_structure not in valid_structures:
            warnings.append(f"Invalid folder_structure '{config.folder_structure}'. Valid options: {valid_structures}")
        
        # Validate output format
        valid_formats = ['obsidian', 'standard']
        if config.output_format not in valid_formats:
            warnings.append(f"Invalid output_format '{config.output_format}'. Valid options: {valid_formats}")
        
        # Check for conflicting settings
        if not config.enable_folder_organization and config.organize_by_folder:
            warnings.append("organize_by_folder is enabled but enable_folder_organization is disabled")
        
        if not config.enable_auto_tagging and (config.custom_tag_rules or config.tag_blacklist):
            warnings.append("Tag rules defined but auto_tagging is disabled")
        
        return warnings