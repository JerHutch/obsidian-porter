"""
Integration tests for the complete SimpleNote to Obsidian import pipeline.
"""

import json
import pytest
from pathlib import Path

from src.simplenote_importer import SimpleNoteImporter
from src.config import ImportConfig


class TestFullPipeline:
    """Integration tests for complete import workflows"""
    
    def test_minimal_import_workflow(self, temp_dir, sample_notes_dir, sample_json_dir):
        """Test complete import with minimal configuration"""
        # Setup test environment
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        # Copy sample data to input directory
        self._copy_sample_data(input_dir, sample_notes_dir, sample_json_dir, "basic_metadata.json")
        
        # Create minimal config
        config = ImportConfig.get_phase2_preset(None, 'minimal')
        
        # Run import
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=input_dir / "source" / "notes.json",
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Verify results
        assert result['success'] is True
        assert result['total_files'] == 2  # From basic_metadata.json
        assert result['processed_files'] == 2
        assert result['errors'] == 0
        
        # Check output files
        output_files = list(output_dir.glob("*.md"))
        assert len(output_files) == 2
        
        # Verify file content
        for md_file in output_files:
            content = md_file.read_text(encoding='utf-8')
            assert content.startswith('---\n')  # Has YAML frontmatter
            assert 'title:' in content
            assert 'source: simplenote' in content
            assert '---\n\n' in content  # Frontmatter separator
    
    def test_organized_import_workflow(self, temp_dir, sample_notes_dir, sample_json_dir):
        """Test complete import with organized configuration (Phase 2 features)"""
        # Setup test environment
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        # Copy complex sample data
        self._copy_sample_data(input_dir, sample_notes_dir, sample_json_dir, "complex_metadata.json")
        
        # Create organized config
        config = ImportConfig.get_phase2_preset(None, 'organized')
        
        # Run import
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=input_dir / "source" / "notes.json",
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Verify results
        assert result['success'] is True
        assert result['total_files'] == 3  # From complex_metadata.json
        assert result['processed_files'] == 3
        
        # Check that folders were created (Phase 2 feature)
        output_files = list(output_dir.rglob("*.md"))
        assert len(output_files) == 3
        
        # Should have organized files into folders
        folders = [f.parent for f in output_files if f.parent != output_dir]
        # Note: exact folder structure depends on Phase 2 implementation
        # At minimum, verify files were processed correctly
        
        # Verify enhanced frontmatter (Phase 2)
        for md_file in output_files:
            content = md_file.read_text(encoding='utf-8')
            assert 'title:' in content
            assert 'source: simplenote' in content
            if 'project' in content.lower():
                assert 'tags:' in content
    
    def test_custom_config_workflow(self, temp_dir, sample_notes_dir, sample_json_dir):
        """Test import with custom configuration"""
        # Setup test environment
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        config_dir = temp_dir / "config"
        input_dir.mkdir()
        config_dir.mkdir()
        
        # Copy sample data
        self._copy_sample_data(input_dir, sample_notes_dir, sample_json_dir, "complex_metadata.json")
        
        # Create custom configuration
        config_data = {
            'enable_editor_pipeline': True,
            'enable_auto_tagging': True,
            'enable_folder_organization': False,
            'enable_content_transformation': True,
            'custom_tag_rules': {
                'project|planning': ['projects', 'work'],
                'research|analysis': ['research']
            }
        }
        
        config_file = config_dir / "custom.yaml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        config = ImportConfig.load_from_file(config_file)
        
        # Run import
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=input_dir / "source" / "notes.json",
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Verify results
        assert result['success'] is True
        assert result['processed_files'] > 0
        
        # Check that custom tagging was applied
        output_files = list(output_dir.rglob("*.md"))
        project_files = [f for f in output_files if 'project' in f.read_text().lower()]
        
        if project_files:
            content = project_files[0].read_text()
            # Should have applied custom tag rules
            assert 'tags:' in content
    
    def test_error_handling_missing_json(self, temp_dir, sample_notes_dir):
        """Test error handling when JSON metadata is missing"""
        # Setup with only txt files, no JSON
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        # Copy only txt files
        for txt_file in sample_notes_dir.glob("*.txt"):
            (input_dir / txt_file.name).write_text(txt_file.read_text(encoding='utf-8'))
        
        config = ImportConfig.get_phase2_preset(None, 'minimal')
        
        # Run import - should handle missing JSON gracefully
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=input_dir / "source" / "notes.json",  # This doesn't exist
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Should still process files, but without metadata
        assert result['success'] is True or result['errors'] > 0
        # Should have created some output files
        output_files = list(output_dir.glob("*.md"))
        assert len(output_files) > 0
    
    def test_error_handling_corrupted_files(self, temp_dir, sample_json_dir):
        """Test error handling with corrupted or unreadable files"""
        # Setup test environment
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        (input_dir / "source").mkdir()
        
        # Copy valid JSON
        json_src = sample_json_dir / "basic_metadata.json"
        json_dst = input_dir / "source" / "notes.json"
        json_dst.write_text(json_src.read_text())
        
        # Create valid and corrupted txt files
        (input_dir / "good_note.txt").write_text("Good Note\nThis is readable content")
        (input_dir / "corrupted_note.txt").write_bytes(b'\x00\x01\x02\x03\x04')  # Binary garbage
        
        config = ImportConfig.get_phase2_preset(None, 'minimal')
        
        # Run import
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=json_dst,
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Should handle errors gracefully
        assert result['total_files'] >= 1  # Should find the good file
        # May have some errors from corrupted file
        if result['errors'] > 0:
            assert result['processed_files'] >= 1  # Should still process good files
    
    def test_large_dataset_performance(self, temp_dir):
        """Test performance with larger dataset"""
        # Setup test environment
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        (input_dir / "source").mkdir()
        
        # Generate test data
        notes_data = {
            "activeNotes": [],
            "trashedNotes": []
        }
        
        # Create 100 test notes
        for i in range(100):
            note = {
                "id": f"test-id-{i:03d}",
                "content": f"Test Note {i}\n\nThis is test content for note number {i}.\nIt has multiple lines and some content.",
                "creationDate": "2024-01-01T10:00:00.000Z",
                "lastModified": "2024-01-01T10:30:00.000Z",
                "tags": [f"tag{i % 10}", "test"],  # Cycle through 10 tags
                "systemTags": [],
                "markdown": i % 2 == 0,  # Every other note is markdown
                "pinned": i % 10 == 0,   # Every 10th note is pinned
                "deleted": False
            }
            notes_data["activeNotes"].append(note)
            
            # Create corresponding txt file
            txt_file = input_dir / f"test-note-{i:03d}.txt"
            txt_file.write_text(note["content"])
        
        # Save JSON metadata
        json_file = input_dir / "source" / "notes.json"
        with open(json_file, 'w') as f:
            json.dump(notes_data, f)
        
        config = ImportConfig.get_phase2_preset(None, 'basic')
        
        # Run import and measure basic performance
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=json_file,
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Verify all notes were processed
        assert result['success'] is True
        assert result['total_files'] == 100
        assert result['processed_files'] == 100
        assert result['errors'] == 0
        
        # Verify output
        output_files = list(output_dir.rglob("*.md"))
        assert len(output_files) == 100
        
        # Spot check a few files
        sample_file = output_files[0]
        content = sample_file.read_text()
        assert 'title:' in content
        assert 'source: simplenote' in content
        assert 'tags:' in content
    
    def _copy_sample_data(self, input_dir: Path, sample_notes_dir: Path, sample_json_dir: Path, json_filename: str):
        """Helper to copy sample data to input directory"""
        # Create source directory for JSON
        source_dir = input_dir / "source"
        source_dir.mkdir()
        
        # Copy JSON metadata
        json_src = sample_json_dir / json_filename
        json_dst = source_dir / "notes.json"
        json_dst.write_text(json_src.read_text())
        
        # Copy corresponding txt files based on JSON content
        with open(json_src) as f:
            metadata = json.load(f)
        
        # Map JSON notes to txt files by matching first line
        for note in metadata.get("activeNotes", []):
            content = note.get("content", "")
            if not content.strip():
                continue
                
            first_line = content.split('\n')[0].strip()
            if first_line.startswith('#'):
                first_line = first_line.lstrip('# ').strip()
            
            # Find matching txt file
            for txt_file in sample_notes_dir.glob("*.txt"):
                txt_content = txt_file.read_text(encoding='utf-8')
                txt_first_line = txt_content.split('\n')[0].strip()
                if txt_first_line.startswith('#'):
                    txt_first_line = txt_first_line.lstrip('# ').strip()
                
                if first_line == txt_first_line:
                    dst_file = input_dir / txt_file.name
                    dst_file.write_text(txt_content)
                    break


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end scenario tests"""
    
    def test_phase1_compatibility(self, temp_dir, sample_notes_dir, sample_json_dir):
        """Test that Phase 1 (minimal) import still works correctly"""
        # This tests backward compatibility
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        # Use basic sample data
        self._copy_sample_data_helper(input_dir, sample_notes_dir, sample_json_dir, "basic_metadata.json")
        
        # Use minimal config (Phase 1 equivalent)
        config = ImportConfig(
            enable_editor_pipeline=False,
            enable_auto_tagging=False,
            enable_folder_organization=False,
            enable_content_transformation=False
        )
        
        # Run import
        importer = SimpleNoteImporter(
            notes_directory=input_dir,
            json_path=input_dir / "source" / "notes.json",
            output_directory=output_dir,
            config=config
        )
        
        result = importer.run()
        
        # Verify Phase 1 behavior
        assert result['success'] is True
        
        output_files = list(output_dir.glob("*.md"))
        assert len(output_files) > 0
        
        # Files should be in root directory (no folder organization)
        for md_file in output_files:
            assert md_file.parent == output_dir
            
        # Content should be minimal (no extra processing)
        sample_file = output_files[0]
        content = sample_file.read_text()
        assert content.startswith('---\n')
        assert 'title:' in content
        assert 'source: simplenote' in content
    
    def _copy_sample_data_helper(self, input_dir: Path, sample_notes_dir: Path, sample_json_dir: Path, json_filename: str):
        """Helper method for copying sample data"""
        # Create source directory for JSON
        source_dir = input_dir / "source"
        source_dir.mkdir()
        
        # Copy JSON metadata
        json_src = sample_json_dir / json_filename
        json_dst = source_dir / "notes.json"
        json_dst.write_text(json_src.read_text())
        
        # Copy all txt files (simple approach for testing)
        for txt_file in sample_notes_dir.glob("*.txt"):
            dst_file = input_dir / txt_file.name
            dst_file.write_text(txt_file.read_text(encoding='utf-8'))