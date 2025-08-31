"""
SimpleNote to Obsidian Importer
Main script for converting SimpleNote exports to Obsidian vault format
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from metadata_parser import MetadataParser
from content_processor import ContentProcessor  
from obsidian_formatter import ObsidianFormatter


class SimpleNoteImporter:
    """Main importer class that orchestrates the conversion process"""
    
    def __init__(self, notes_directory: Path, json_path: Optional[Path] = None, output_directory: Optional[Path] = None):
        """
        Initialize the importer
        
        Args:
            notes_directory: Directory containing .txt note files
            json_path: Path to notes.json file (optional)
            output_directory: Output directory for Obsidian notes
        """
        self.notes_directory = Path(notes_directory)
        self.json_path = Path(json_path) if json_path else None
        self.output_directory = Path(output_directory) if output_directory else self.notes_directory / "obsidian_vault"
        
        # Initialize processors
        self.content_processor = ContentProcessor(self.notes_directory)
        self.obsidian_formatter = ObsidianFormatter(self.output_directory)
        self.metadata_parser = MetadataParser(self.json_path) if self.json_path else None
        
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
            
            # Step 3: Format and save to Obsidian
            print("Step 3: Formatting and saving notes for Obsidian...")
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


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Convert SimpleNote export to Obsidian vault format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic import from current directory
  python simplenote_importer.py

  # Import with custom paths
  python simplenote_importer.py --notes /path/to/notes --output /path/to/vault

  # Import with metadata
  python simplenote_importer.py --notes /path/to/notes --json /path/to/source/notes.json
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
    
    args = parser.parse_args()
    
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
        output_directory=args.output
    )
    
    success = importer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()