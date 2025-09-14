"""
Unit tests for SimpleNoteImporter main class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.simplenote_importer import SimpleNoteImporter
from src.config import ImportConfig
from src.interfaces.file_system import MockFileSystem


class TestSimpleNoteImporter:
    """Test cases for SimpleNoteImporter class"""
    
    def test_init_default(self, tmp_path):
        """Test SimpleNoteImporter initialization with defaults"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        importer = SimpleNoteImporter(notes_directory=notes_dir)
        
        assert importer.notes_directory == notes_dir
        assert importer.json_path is None
        assert importer.output_directory == notes_dir / "obsidian_vault"
        assert isinstance(importer.config, ImportConfig)
        assert importer.metadata_parser is None
        assert importer.content_processor is not None
        assert importer.obsidian_formatter is not None
    
    def test_init_with_json_path(self, tmp_path):
        """Test SimpleNoteImporter initialization with JSON path"""
        notes_dir = tmp_path / "notes"
        json_path = tmp_path / "notes.json"
        notes_dir.mkdir()
        json_path.touch()
        
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            json_path=json_path
        )
        
        assert importer.json_path == json_path
        assert importer.metadata_parser is not None
    
    def test_init_with_custom_config(self, tmp_path):
        """Test SimpleNoteImporter initialization with custom config"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        config = ImportConfig(
            enable_editor_pipeline=True,
            enable_auto_tagging=False,
            enable_folder_organization=True
        )
        
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            config=config
        )
        
        assert importer.config == config
        assert importer.config.enable_auto_tagging is False
        assert importer.config.enable_folder_organization is True
    
    def test_init_with_editor_pipeline_enabled(self, tmp_path):
        """Test initialization with editor pipeline enabled"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        config = ImportConfig(enable_editor_pipeline=True)
        
        with patch.object(SimpleNoteImporter, '_setup_editor_pipeline') as mock_setup:
            mock_pipeline = Mock()
            mock_setup.return_value = mock_pipeline
            
            importer = SimpleNoteImporter(
                notes_directory=notes_dir,
                config=config
            )
            
            assert importer.editor_pipeline == mock_pipeline
            mock_setup.assert_called_once()
    
    def test_init_with_editor_pipeline_disabled(self, tmp_path):
        """Test initialization with editor pipeline disabled"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        config = ImportConfig(enable_editor_pipeline=False)
        
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            config=config
        )
        
        assert importer.editor_pipeline is None
    
    def test_init_with_file_system(self, tmp_path):
        """Test initialization with custom file system"""
        notes_dir = tmp_path / "notes"
        mock_file_system = MockFileSystem()
        
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            file_system=mock_file_system
        )
        
        assert importer.file_system == mock_file_system
    
    def test_setup_editor_pipeline_all_processors(self):
        """Test editor pipeline setup with all processors enabled"""
        config = ImportConfig(
            enable_editor_pipeline=True,
            enable_auto_tagging=True,
            enable_folder_organization=True,
            enable_content_transformation=True,
            enable_note_splitting=True
        )
        
        with patch('src.simplenote_importer.EditorPipeline') as mock_pipeline_class, \
             patch('src.simplenote_importer.TagInjector') as mock_tag_injector, \
             patch('src.simplenote_importer.FolderOrganizer') as mock_folder_organizer, \
             patch('src.simplenote_importer.ContentTransformer') as mock_content_transformer, \
             patch('src.simplenote_importer.NoteSplitter') as mock_note_splitter:
            
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            
            importer = SimpleNoteImporter(Path("/tmp"), config=config)
            pipeline = importer._setup_editor_pipeline()
            
            # Should create all processor types
            mock_tag_injector.assert_called_once()
            mock_folder_organizer.assert_called_once()
            mock_content_transformer.assert_called_once()
            mock_note_splitter.assert_called_once()
            
            # Should add all processors to pipeline
            assert mock_pipeline.add_processor.call_count == 4
    
    def test_setup_editor_pipeline_selective_processors(self):
        """Test editor pipeline setup with selective processors"""
        config = ImportConfig(
            enable_editor_pipeline=True,
            enable_auto_tagging=True,
            enable_folder_organization=False,
            enable_content_transformation=True,
            enable_note_splitting=False
        )
        
        with patch('src.simplenote_importer.EditorPipeline') as mock_pipeline_class, \
             patch('src.simplenote_importer.TagInjector') as mock_tag_injector, \
             patch('src.simplenote_importer.FolderOrganizer') as mock_folder_organizer, \
             patch('src.simplenote_importer.ContentTransformer') as mock_content_transformer, \
             patch('src.simplenote_importer.NoteSplitter') as mock_note_splitter:
            
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            
            importer = SimpleNoteImporter(Path("/tmp"), config=config)
            pipeline = importer._setup_editor_pipeline()
            
            # Should create only enabled processors
            mock_tag_injector.assert_called_once()
            mock_folder_organizer.assert_not_called()
            mock_content_transformer.assert_called_once()
            mock_note_splitter.assert_not_called()
            
            # Should add only enabled processors
            assert mock_pipeline.add_processor.call_count == 2
    
    @patch('builtins.print')
    def test_run_success_without_json(self, mock_print, tmp_path):
        """Test successful run without JSON metadata"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        # Setup mocks
        mock_notes = [
            {'filename': 'note1.txt', 'content': 'Content 1'},
            {'filename': 'note2.txt', 'content': 'Content 2'}
        ]
        mock_saved_files = {'note1.txt': 'path1', 'note2.txt': 'path2'}
        
        with patch.object(SimpleNoteImporter, '__init__', return_value=None):
            importer = SimpleNoteImporter.__new__(SimpleNoteImporter)
            importer.notes_directory = notes_dir
            importer.json_path = None
            importer.output_directory = notes_dir / "obsidian_vault"
            importer.config = ImportConfig(enable_editor_pipeline=False)
            importer.metadata_parser = None
            importer.editor_pipeline = None
            
            # Mock processors
            importer.content_processor = Mock()
            importer.content_processor.process_all_notes.return_value = mock_notes
            
            importer.obsidian_formatter = Mock()
            importer.obsidian_formatter.save_all_notes.return_value = mock_saved_files
            
            result = importer.run()
            
            assert isinstance(result, dict) and result.get('success') is True
            importer.content_processor.process_all_notes.assert_called_once()
            importer.obsidian_formatter.save_all_notes.assert_called_once_with(mock_notes, {})
    
    @patch('builtins.print')
    def test_run_success_with_json(self, mock_print, tmp_path):
        """Test successful run with JSON metadata"""
        notes_dir = tmp_path / "notes"
        json_path = tmp_path / "notes.json"
        notes_dir.mkdir()
        json_path.touch()
        
        # Setup test data
        mock_notes = [{'filename': 'note1.txt', 'content': 'Content 1'}]
        mock_metadata_map = {'note1.txt': {'tags': ['test'], 'created': '2024-01-01'}}
        mock_saved_files = {'note1.txt': 'path1'}
        
        with patch.object(SimpleNoteImporter, '__init__', return_value=None):
            importer = SimpleNoteImporter.__new__(SimpleNoteImporter)
            importer.notes_directory = notes_dir
            importer.json_path = json_path
            importer.output_directory = notes_dir / "obsidian_vault"
            importer.config = ImportConfig(enable_editor_pipeline=False)
            importer.editor_pipeline = None
            
            # Mock processors
            importer.metadata_parser = Mock()
            importer.metadata_parser.parse.return_value = mock_metadata_map
            
            importer.content_processor = Mock()
            importer.content_processor.process_all_notes.return_value = mock_notes
            
            importer.obsidian_formatter = Mock()
            importer.obsidian_formatter.save_all_notes.return_value = mock_saved_files
            
            result = importer.run()
            
            assert isinstance(result, dict) and result.get('success') is True
            importer.metadata_parser.parse.assert_called_once()
            importer.obsidian_formatter.save_all_notes.assert_called_once_with(mock_notes, mock_metadata_map)
    
    @patch('builtins.print')
    def test_run_with_editor_pipeline(self, mock_print, tmp_path):
        """Test run with editor pipeline enabled"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        mock_notes = [{'filename': 'note1.txt', 'content': 'Original content'}]
        mock_metadata_map = {'note1.txt': {'tags': ['original']}}
        mock_processed_metadata = {'tags': ['original', 'processed']}
        
        with patch.object(SimpleNoteImporter, '__init__', return_value=None):
            importer = SimpleNoteImporter.__new__(SimpleNoteImporter)
            importer.notes_directory = notes_dir
            importer.json_path = None
            importer.output_directory = notes_dir / "obsidian_vault"
            importer.config = ImportConfig(enable_editor_pipeline=True, enable_note_splitting=False)
            
            # Mock processors
            importer.content_processor = Mock()
            importer.content_processor.process_all_notes.return_value = mock_notes
            
            importer.metadata_parser = None
            
            importer.editor_pipeline = Mock()
            importer.editor_pipeline.process.return_value = ("Processed content", mock_processed_metadata)
            
            importer.obsidian_formatter = Mock()
            importer.obsidian_formatter.save_all_notes.return_value = {'note1.txt': 'path1'}
            
            result = importer.run()
            
            assert isinstance(result, dict) and result.get('success') is True
            importer.editor_pipeline.process.assert_called_once_with(
                'Original content', {}, {
                    'filename': 'note1.txt',
                    'original_path': None,
                    'phase': 2
                }
            )
    
    @patch('builtins.print')
    def test_run_with_note_splitting(self, mock_print, tmp_path):
        """Test run with note splitting enabled"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        mock_notes = [{'filename': 'note1.txt', 'content': 'Original content'}]
        mock_split_notes = [
            {'filename': 'note1.txt', 'content': 'Part 1', 'metadata': {'tags': ['part1']}},
            {'filename': 'note1-part2.txt', 'content': 'Part 2', 'metadata': {'tags': ['part2']}}
        ]
        
        with patch.object(SimpleNoteImporter, '__init__', return_value=None):
            importer = SimpleNoteImporter.__new__(SimpleNoteImporter)
            importer.notes_directory = notes_dir
            importer.json_path = None
            importer.output_directory = notes_dir / "obsidian_vault"
            importer.config = ImportConfig(enable_editor_pipeline=True, enable_note_splitting=True)
            
            # Mock processors
            importer.content_processor = Mock()
            importer.content_processor.process_all_notes.return_value = mock_notes
            
            importer.metadata_parser = None
            
            # Mock note splitter
            mock_note_splitter = Mock()
            mock_note_splitter.get_split_notes.return_value = mock_split_notes
            
            importer.editor_pipeline = Mock()
            importer.editor_pipeline.process.return_value = ("Processed content", {'tags': ['processed']})
            importer.editor_pipeline.get_note_splitter.return_value = mock_note_splitter
            
            importer.obsidian_formatter = Mock()
            importer.obsidian_formatter.save_all_notes.return_value = {'note1.txt': 'path1', 'note1-part2.txt': 'path2'}
            
            result = importer.run()
            
            assert isinstance(result, dict) and result.get('success') is True
            
            # Should process split notes
            expected_metadata_map = {
                'note1.txt': {'tags': ['part1']},
                'note1-part2.txt': {'tags': ['part2']}
            }
            
            # Check that save_all_notes was called with split notes
            call_args = importer.obsidian_formatter.save_all_notes.call_args
            saved_notes = call_args[0][0]
            saved_metadata = call_args[0][1]
            
            assert len(saved_notes) == 2
            assert saved_metadata == expected_metadata_map
    
    @patch('builtins.print')
    def test_run_no_notes_found(self, mock_print, tmp_path):
        """Test run when no notes are found"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        with patch.object(SimpleNoteImporter, '__init__', return_value=None):
            importer = SimpleNoteImporter.__new__(SimpleNoteImporter)
            importer.notes_directory = notes_dir
            importer.json_path = None
            importer.output_directory = notes_dir / "obsidian_vault"
            importer.config = ImportConfig(enable_editor_pipeline=False)
            importer.metadata_parser = None
            importer.editor_pipeline = None
            
            # Mock processors
            importer.content_processor = Mock()
            importer.content_processor.process_all_notes.return_value = []
            
            result = importer.run()
            
            assert isinstance(result, dict) and result.get('success') is False
            mock_print.assert_any_call("No notes found to process!")
    
    @patch('builtins.print')
    def test_run_exception_handling(self, mock_print, tmp_path):
        """Test run handles exceptions properly"""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        with patch.object(SimpleNoteImporter, '__init__', return_value=None):
            importer = SimpleNoteImporter.__new__(SimpleNoteImporter)
            importer.notes_directory = notes_dir
            importer.json_path = None
            importer.output_directory = notes_dir / "obsidian_vault"
            importer.config = ImportConfig(enable_editor_pipeline=False)
            importer.metadata_parser = None
            importer.editor_pipeline = None
            
            # Mock processors to raise exception
            importer.content_processor = Mock()
            importer.content_processor.process_all_notes.side_effect = Exception("Test error")
            
            with patch('traceback.print_exc') as mock_traceback:
                result = importer.run()
                
                assert isinstance(result, dict) and result.get('success') is False
                mock_print.assert_any_call("Error during import: Test error")
                mock_traceback.assert_called_once()
    
    @patch('builtins.print')
    def test_print_summary(self, mock_print):
        """Test _print_summary method"""
        importer = SimpleNoteImporter(Path("/tmp"))
        importer.output_directory = Path("/output")
        
        notes = [{'filename': 'note1.txt'}, {'filename': 'note2.txt'}]
        metadata_map = {'note1.txt': {'tags': ['test']}}
        saved_files = {'note1.txt': 'path1', 'note2.txt': 'path2'}
        
        importer._print_summary(notes, metadata_map, saved_files)
        
        mock_print.assert_any_call("=== Import Summary ===")
        mock_print.assert_any_call("Total notes processed: 2")
        mock_print.assert_any_call("Notes with metadata: 1")
        mock_print.assert_any_call("Notes successfully saved: 2")
        mock_print.assert_any_call("Output location: /output")
        mock_print.assert_any_call("\nImport completed!")
    
    @patch('builtins.print')
    def test_print_summary_with_failures(self, mock_print):
        """Test _print_summary with save failures"""
        importer = SimpleNoteImporter(Path("/tmp"))
        
        notes = [{'filename': 'note1.txt'}, {'filename': 'note2.txt'}, {'filename': 'note3.txt'}]
        metadata_map = {}
        saved_files = {'note1.txt': 'path1'}  # Only one saved successfully
        
        importer._print_summary(notes, metadata_map, saved_files)
        
        mock_print.assert_any_call("Warning: 2 notes failed to save")
    
    @pytest.mark.integration  
    def test_end_to_end_minimal_setup(self, tmp_path):
        """Integration test with minimal setup"""
        # Setup test files
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        
        note_file = notes_dir / "test_note.txt"
        note_file.write_text("This is a test note\nWith some content.")
        
        # Create importer with minimal config
        config = ImportConfig(enable_editor_pipeline=False)
        
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            config=config
        )
        
        # Run import
        with patch('builtins.print'):  # Suppress output for test
            result = importer.run()
        
        assert isinstance(result, dict) and result.get('success') is True
        
        # Check output was created
        output_dir = notes_dir / "obsidian_vault"
        assert output_dir.exists()
    
    @pytest.mark.edge_case
    def test_init_with_nonexistent_directories(self):
        """Test initialization with non-existent directories"""
        notes_dir = Path("/nonexistent/notes")
        json_path = Path("/nonexistent/notes.json")
        
        # Should not raise exception during init
        importer = SimpleNoteImporter(
            notes_directory=notes_dir,
            json_path=json_path
        )
        
        assert importer.notes_directory == notes_dir
        assert importer.json_path == json_path
    
    @pytest.mark.edge_case
    def test_setup_editor_pipeline_with_custom_rules(self):
        """Test editor pipeline setup with custom rules"""
        custom_tag_rules = {'project': ['work']}
        custom_folder_rules = {'work': 'work_folder'}
        custom_transformations = {'old': 'new'}
        
        config = ImportConfig(
            enable_editor_pipeline=True,
            enable_auto_tagging=True,
            enable_folder_organization=True,
            enable_content_transformation=True,
            custom_tag_rules=custom_tag_rules,
            custom_folder_rules=custom_folder_rules,
            custom_transformations=custom_transformations
        )
        
        with patch('src.simplenote_importer.EditorPipeline') as mock_pipeline_class, \
             patch('src.simplenote_importer.TagInjector') as mock_tag_injector_class, \
             patch('src.simplenote_importer.FolderOrganizer') as mock_folder_organizer_class, \
             patch('src.simplenote_importer.ContentTransformer') as mock_content_transformer_class:
            
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            
            mock_tag_injector = Mock()
            mock_tag_injector_class.return_value = mock_tag_injector
            
            mock_folder_organizer = Mock()
            mock_folder_organizer.organization_rules = {}
            mock_folder_organizer_class.return_value = mock_folder_organizer
            
            mock_content_transformer = Mock()
            mock_content_transformer.transformation_rules = {}
            mock_content_transformer_class.return_value = mock_content_transformer
            
            importer = SimpleNoteImporter(Path("/tmp"), config=config)
            
            # Should pass custom rules to processors
            mock_tag_injector_class.assert_called_with(tag_rules=custom_tag_rules)
            # Folder rules should be merged
            assert all(item in mock_folder_organizer.organization_rules.items() for item in custom_folder_rules.items())
            mock_content_transformer.transformation_rules.update.assert_called_with(custom_transformations)
    
    def test_main_function_imports(self):
        """Test that main function and CLI imports work correctly"""
        # This test ensures the main function can be imported without errors
        from src.simplenote_importer import main
        assert callable(main)