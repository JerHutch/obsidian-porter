"""
SimpleNote to Obsidian Importer
Main script for converting SimpleNote exports to Obsidian vault format
Phase 2: Enhanced with editor pipeline and configuration support
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from metadata_parser import MetadataParser
from content_processor import ContentProcessor  
from obsidian_formatter import ObsidianFormatter
from editor_pipeline import EditorPipeline
from config import ImportConfig, ConfigManager


class SimpleNoteImporter:
    """Main importer class that orchestrates the conversion process"""
    
    def __init__(self, notes_directory: Path, json_path: Optional[Path] = None, output_directory: Optional[Path] = None, config: Optional[ImportConfig] = None):
        """
        Initialize the importer
        
        Args:
            notes_directory: Directory containing .txt note files
            json_path: Path to notes.json file (optional)
            output_directory: Output directory for Obsidian notes
            config: Import configuration (Phase 2)
        """
        self.notes_directory = Path(notes_directory)
        self.json_path = Path(json_path) if json_path else None
        self.output_directory = Path(output_directory) if output_directory else self.notes_directory / "obsidian_vault"
        self.config = config or ImportConfig()
        
        # Initialize processors
        self.content_processor = ContentProcessor(self.notes_directory)
        self.obsidian_formatter = ObsidianFormatter(self.output_directory)
        self.metadata_parser = MetadataParser(self.json_path) if self.json_path else None
        
        # Initialize Phase 2 components
        self.editor_pipeline = None
        if self.config.enable_editor_pipeline:
            self.editor_pipeline = self._setup_editor_pipeline()
        
    def run(self) -> bool:
        """
        Run the complete import process
        
        Returns:
            True if successful, False if errors occurred
        """
        try:
            print("=== SimpleNote to Obsidian Importer ===")
            print(f"Notes directory: {self.notes_directory}")
            print(f"JSON metadata: {self.json_path or 'Not provided'}")
            print(f"Output directory: {self.output_directory}")
            print()
            
            # Step 1: Parse metadata (if available)
            metadata_map = {}
            if self.metadata_parser:
                print("Step 1: Parsing metadata from JSON...")
                metadata_map = self.metadata_parser.parse()
                print(f"Parsed metadata for {len(metadata_map)} notes")
            else:
                print("Step 1: Skipping metadata parsing (no JSON file provided)")
            print()
            
            # Step 2: Process .txt files
            print("Step 2: Processing .txt files...")
            notes = self.content_processor.process_all_notes()
            print(f"Processed {len(notes)} note files")
            print()
            
            if not notes:
                print("No notes found to process!")
                return False
            
            # Step 3: Apply editor pipeline (Phase 2)
            if self.editor_pipeline:
                print("Step 3: Applying editor pipeline transformations...")
                processed_notes = []
                for note in notes:
                    original_filename = note.get('filename', '')
                    original_metadata = metadata_map.get(original_filename, {})
                    
                    # Create processing context
                    context = {
                        'filename': original_filename,
                        'original_path': note.get('original_path'),
                        'phase': 2
                    }
                    
                    # Apply pipeline
                    processed_content, processed_metadata = self.editor_pipeline.process(
                        note['content'], original_metadata, context
                    )
                    
                    # Update note with processed content
                    processed_note = note.copy()
                    processed_note['content'] = processed_content
                    processed_notes.append(processed_note)
                    
                    # Update metadata map
                    metadata_map[original_filename] = processed_metadata
                
                notes = processed_notes
                print(f"Processed {len(notes)} notes through editor pipeline")
                print()
            
            # Step 4: Format and save to Obsidian
            step_num = 4 if self.editor_pipeline else 3
            print(f"Step {step_num}: Formatting and saving notes for Obsidian...")
            saved_files = self.obsidian_formatter.save_all_notes(notes, metadata_map)
            print(f"Successfully saved {len(saved_files)} notes")
            print()
            
            # Summary
            self._print_summary(notes, metadata_map, saved_files)
            return True
            
        except Exception as e:
            print(f"Error during import: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _print_summary(self, notes: list, metadata_map: dict, saved_files: dict):
        """Print import summary"""
        print("=== Import Summary ===")
        print(f"Total notes processed: {len(notes)}")
        print(f"Notes with metadata: {len(metadata_map)}")
        print(f"Notes successfully saved: {len(saved_files)}")
        print(f"Output location: {self.output_directory}")
        
        if len(notes) != len(saved_files):
            print(f"Warning: {len(notes) - len(saved_files)} notes failed to save")
            
        print("\nImport completed!")
    
    def _setup_editor_pipeline(self) -> EditorPipeline:
        """Setup editor pipeline with configured processors"""
        from editor_pipeline import EditorPipeline, TagInjector, FolderOrganizer, ContentTransformer
        
        pipeline = EditorPipeline()
        
        # Add processors based on configuration
        if self.config.enable_auto_tagging:
            tag_injector = TagInjector()
            # Apply custom tag rules if configured
            if self.config.custom_tag_rules:
                tag_injector.tag_rules.update(self.config.custom_tag_rules)
            pipeline.add_processor(tag_injector)
        
        if self.config.enable_folder_organization:
            folder_organizer = FolderOrganizer()
            # Apply custom folder rules if configured
            if self.config.custom_folder_rules:
                folder_organizer.organization_rules.update(self.config.custom_folder_rules)
            pipeline.add_processor(folder_organizer)
        
        if self.config.enable_content_transformation:
            content_transformer = ContentTransformer()
            # Apply custom transformations if configured
            if self.config.custom_transformations:
                content_transformer.transformation_rules.update(self.config.custom_transformations)
            pipeline.add_processor(content_transformer)
        
        return pipeline


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Convert SimpleNote export to Obsidian vault format with smart processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic import from current directory
  python simplenote_importer.py

  # Import with custom paths  
  python simplenote_importer.py --notes /path/to/notes --output /path/to/vault

  # Import with metadata and smart processing
  python simplenote_importer.py --notes /path/to/notes --json /path/to/source/notes.json --smart

  # Import with configuration preset
  python simplenote_importer.py --preset organized

  # Import with custom config file
  python simplenote_importer.py --config config/my_settings.yaml
        """
    )
    
    parser.add_argument(
        '--notes',
        type=Path,
        default=Path.cwd(),
        help='Directory containing .txt note files (default: current directory)'
    )
    
    parser.add_argument(
        '--json',
        type=Path,
        help='Path to notes.json file for metadata (optional)'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory for Obsidian vault (default: notes_dir/obsidian_vault)'
    )
    
    # Smart processing options
    parser.add_argument(
        '--smart',
        action='store_true',
        help='Enable smart processing (auto-tagging, folder organization, content transformation)'
    )
    
    parser.add_argument(
        '--preset',
        choices=['minimal', 'basic', 'organized', 'full'],
        help='Use a configuration preset (minimal, basic, organized, full)'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file (YAML or JSON)'
    )
    
    parser.add_argument(
        '--create-sample-config',
        action='store_true',
        help='Create a sample configuration file and exit'
    )
    
    args = parser.parse_args()
    
    # Handle sample config creation
    if args.create_sample_config:
        config_manager = ConfigManager()
        config_manager.create_sample_config()
        return
    
    # Setup configuration
    config = None
    
    if args.preset:
        config = ImportConfig().get_phase2_preset(args.preset)
        print(f"Using configuration preset: {args.preset}")
    elif args.config:
        if not args.config.exists():
            print(f"Error: Configuration file does not exist: {args.config}")
            sys.exit(1)
        config = ImportConfig.load_from_file(args.config)
        print(f"Using configuration file: {args.config}")
    elif args.smart:
        config = ImportConfig()  # Default smart processing config
        print("Using default smart processing configuration")
    else:
        # Phase 1 compatibility mode
        config = ImportConfig().get_phase2_preset('minimal')
        print("Using Phase 1 compatibility mode")
    
    # Validate configuration
    if config:
        config_manager = ConfigManager()
        warnings = config_manager.validate_config(config)
        for warning in warnings:
            print(f"Configuration warning: {warning}")
    
    # Validate inputs
    if not args.notes.exists():
        print(f"Error: Notes directory does not exist: {args.notes}")
        sys.exit(1)
        
    if args.json and not args.json.exists():
        print(f"Error: JSON file does not exist: {args.json}")
        sys.exit(1)
    
    # Run import
    importer = SimpleNoteImporter(
        notes_directory=args.notes,
        json_path=args.json,
        output_directory=args.output,
        config=config
    )
    
    success = importer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()