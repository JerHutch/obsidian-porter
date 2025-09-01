"""
Unit tests for Configuration classes.
"""

import pytest
import json
import yaml
from pathlib import Path

from src.config import ImportConfig, ConfigManager


class TestImportConfig:
    """Test cases for ImportConfig class"""
    
    def test_init_default(self):
        """Test ImportConfig initialization with defaults"""
        config = ImportConfig()
        
        # Phase 2 features should be enabled by default
        assert config.enable_editor_pipeline is True
        assert config.enable_auto_tagging is True
        assert config.enable_folder_organization is True
        assert config.enable_content_transformation is True
        
        # Phase 3 features should be disabled by default
        assert config.enable_note_splitting is False
        
        # Default settings
        assert config.organize_by_folder is True
        assert config.folder_structure == "tags"
        assert config.output_format == "obsidian"
    
    def test_init_custom_values(self):
        """Test ImportConfig initialization with custom values"""
        config = ImportConfig(
            enable_editor_pipeline=False,
            enable_auto_tagging=False,
            folder_structure="date",
            output_format="standard"
        )
        
        assert config.enable_editor_pipeline is False
        assert config.enable_auto_tagging is False
        assert config.folder_structure == "date"
        assert config.output_format == "standard"
    
    def test_load_from_yaml_file(self, temp_dir):
        """Test loading configuration from YAML file"""
        config_data = {
            'enable_editor_pipeline': False,
            'enable_auto_tagging': True,
            'folder_structure': 'custom',
            'custom_tag_rules': {
                'pattern1': ['tag1', 'tag2'],
                'pattern2': ['tag3']
            }
        }
        
        config_file = temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = ImportConfig.load_from_file(config_file)
        
        assert config.enable_editor_pipeline is False
        assert config.enable_auto_tagging is True
        assert config.folder_structure == 'custom'
        assert config.custom_tag_rules == {
            'pattern1': ['tag1', 'tag2'],
            'pattern2': ['tag3']
        }
    
    def test_load_from_json_file(self, temp_dir):
        """Test loading configuration from JSON file"""
        config_data = {
            'enable_editor_pipeline': True,
            'enable_folder_organization': False,
            'output_format': 'standard'
        }
        
        config_file = temp_dir / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = ImportConfig.load_from_file(config_file)
        
        assert config.enable_editor_pipeline is True
        assert config.enable_folder_organization is False
        assert config.output_format == 'standard'
    
    def test_load_from_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file returns default config"""
        config_file = temp_dir / "nonexistent.yaml"
        config = ImportConfig.load_from_file(config_file)
        
        # Should return default configuration
        assert config.enable_editor_pipeline is True
        assert config.enable_auto_tagging is True
    
    def test_load_from_invalid_file(self, temp_dir):
        """Test loading from invalid file returns default config"""
        config_file = temp_dir / "invalid.yaml"
        with open(config_file, 'w') as f:
            f.write("{ invalid yaml content }")
        
        config = ImportConfig.load_from_file(config_file)
        
        # Should return default configuration on error
        assert config.enable_editor_pipeline is True
        assert config.enable_auto_tagging is True
    
    def test_save_to_file(self, temp_dir):
        """Test saving configuration to file"""
        config = ImportConfig(
            enable_editor_pipeline=False,
            enable_auto_tagging=True,
            custom_tag_rules={'test': ['tag1']}
        )
        
        config_file = temp_dir / "saved_config.yaml"
        config.save_to_file(config_file)
        
        assert config_file.exists()
        
        # Load and verify
        with open(config_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data['enable_editor_pipeline'] is False
        assert saved_data['enable_auto_tagging'] is True
        assert saved_data['custom_tag_rules'] == {'test': ['tag1']}
    
    def test_save_creates_directory(self, temp_dir):
        """Test that save_to_file creates parent directories"""
        config = ImportConfig()
        config_file = temp_dir / "subdir" / "config.yaml"
        
        config.save_to_file(config_file)
        
        assert config_file.exists()
        assert config_file.parent.exists()
    
    def test_get_phase2_preset_minimal(self):
        """Test getting minimal preset"""
        config = ImportConfig()
        preset = config.get_phase2_preset('minimal')
        
        assert preset.enable_editor_pipeline is False
        assert preset.enable_auto_tagging is False
        assert preset.enable_folder_organization is False
        assert preset.enable_content_transformation is False
        assert preset.organize_by_folder is False
    
    def test_get_phase2_preset_basic(self):
        """Test getting basic preset"""
        config = ImportConfig()
        preset = config.get_phase2_preset('basic')
        
        assert preset.enable_editor_pipeline is True
        assert preset.enable_auto_tagging is True
        assert preset.enable_folder_organization is False
        assert preset.enable_content_transformation is True
        assert preset.organize_by_folder is False
    
    def test_get_phase2_preset_organized(self):
        """Test getting organized preset"""
        config = ImportConfig()
        preset = config.get_phase2_preset('organized')
        
        assert preset.enable_editor_pipeline is True
        assert preset.enable_auto_tagging is True
        assert preset.enable_folder_organization is True
        assert preset.enable_content_transformation is True
        assert preset.organize_by_folder is True
        assert preset.folder_structure == "tags"
        assert preset.create_index_files is False
    
    def test_get_phase2_preset_full(self):
        """Test getting full preset"""
        config = ImportConfig()
        preset = config.get_phase2_preset('full')
        
        assert preset.enable_editor_pipeline is True
        assert preset.enable_auto_tagging is True
        assert preset.enable_folder_organization is True
        assert preset.enable_content_transformation is True
        assert preset.organize_by_folder is True
        assert preset.create_index_files is True
        assert preset.create_backlinks is True
    
    def test_get_phase2_preset_phase3(self):
        """Test getting Phase 3 preset"""
        config = ImportConfig()
        preset = config.get_phase2_preset('phase3')
        
        assert preset.enable_note_splitting is True
        assert preset.split_header_level == 2
        assert preset.preserve_main_header is True
    
    def test_get_phase2_preset_invalid(self):
        """Test getting invalid preset returns default"""
        config = ImportConfig()
        preset = config.get_phase2_preset('invalid_preset')
        
        # Should return default configuration
        assert preset.enable_editor_pipeline is True
        assert preset.enable_auto_tagging is True


class TestConfigManager:
    """Test cases for ConfigManager class"""
    
    def test_init_default(self, temp_dir):
        """Test ConfigManager initialization with default directory"""
        manager = ConfigManager()
        
        assert manager.config_dir == Path.cwd() / "config"
        assert manager.default_config_file == Path.cwd() / "config" / "import_config.yaml"
    
    def test_init_custom_dir(self, temp_dir):
        """Test ConfigManager initialization with custom directory"""
        config_dir = temp_dir / "custom_config"
        manager = ConfigManager(config_dir)
        
        assert manager.config_dir == config_dir
        assert manager.default_config_file == config_dir / "import_config.yaml"
        assert config_dir.exists()
    
    def test_load_config_default(self, temp_dir):
        """Test loading default configuration"""
        manager = ConfigManager(temp_dir)
        config = manager.load_config()
        
        # Should return default config since no file exists
        assert isinstance(config, ImportConfig)
        assert config.enable_editor_pipeline is True
    
    def test_load_config_from_file(self, temp_dir):
        """Test loading configuration from specific file"""
        config_data = {
            'enable_editor_pipeline': False,
            'folder_structure': 'date'
        }
        
        config_file = temp_dir / "custom.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(temp_dir)
        config = manager.load_config(config_file)
        
        assert config.enable_editor_pipeline is False
        assert config.folder_structure == 'date'
    
    def test_save_config(self, temp_dir):
        """Test saving configuration"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(
            enable_editor_pipeline=False,
            enable_auto_tagging=True
        )
        
        config_file = temp_dir / "saved.yaml"
        manager.save_config(config, config_file)
        
        assert config_file.exists()
        
        # Verify saved content
        loaded_config = manager.load_config(config_file)
        assert loaded_config.enable_editor_pipeline is False
        assert loaded_config.enable_auto_tagging is True
    
    def test_save_config_default_file(self, temp_dir):
        """Test saving to default config file"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(enable_editor_pipeline=False)
        
        manager.save_config(config)
        
        assert manager.default_config_file.exists()
        
        # Verify we can load it back
        loaded_config = manager.load_config()
        assert loaded_config.enable_editor_pipeline is False
    
    def test_create_sample_config(self, temp_dir):
        """Test creating sample configuration file"""
        manager = ConfigManager(temp_dir)
        sample_file = temp_dir / "sample.yaml"
        
        manager.create_sample_config(sample_file)
        
        assert sample_file.exists()
        
        # Check that it contains expected content
        content = sample_file.read_text()
        assert 'enable_editor_pipeline' in content
        assert 'custom_tag_rules' in content
        assert 'Phase 2 Features' in content
    
    def test_create_sample_config_default_location(self, temp_dir):
        """Test creating sample config at default location"""
        manager = ConfigManager(temp_dir)
        
        manager.create_sample_config()
        
        expected_file = temp_dir / "sample_config.yaml"
        assert expected_file.exists()
    
    def test_validate_config_valid(self, temp_dir):
        """Test validating valid configuration"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(
            folder_structure='tags',
            output_format='obsidian'
        )
        
        warnings = manager.validate_config(config)
        assert len(warnings) == 0
    
    def test_validate_config_invalid_folder_structure(self, temp_dir):
        """Test validating config with invalid folder structure"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(folder_structure='invalid_structure')
        
        warnings = manager.validate_config(config)
        assert len(warnings) > 0
        assert any('folder_structure' in warning for warning in warnings)
    
    def test_validate_config_invalid_output_format(self, temp_dir):
        """Test validating config with invalid output format"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(output_format='invalid_format')
        
        warnings = manager.validate_config(config)
        assert len(warnings) > 0
        assert any('output_format' in warning for warning in warnings)
    
    def test_validate_config_conflicting_settings(self, temp_dir):
        """Test validating config with conflicting settings"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(
            enable_folder_organization=False,
            organize_by_folder=True
        )
        
        warnings = manager.validate_config(config)
        assert len(warnings) > 0
        assert any('organize_by_folder' in warning for warning in warnings)
    
    def test_validate_config_disabled_auto_tagging_with_rules(self, temp_dir):
        """Test validating config with tagging disabled but rules defined"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig(
            enable_auto_tagging=False,
            custom_tag_rules={'pattern': ['tag']},
            tag_blacklist=['blocked_tag']
        )
        
        warnings = manager.validate_config(config)
        assert len(warnings) > 0
        assert any('auto_tagging' in warning.lower() for warning in warnings)
    
    @pytest.mark.edge_case
    def test_load_config_with_unknown_fields(self, temp_dir):
        """Test loading config with unknown fields (should be ignored)"""
        config_data = {
            'enable_editor_pipeline': True,
            'unknown_field': 'unknown_value',
            'another_unknown': 123
        }
        
        config_file = temp_dir / "unknown_fields.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(temp_dir)
        config = manager.load_config(config_file)
        
        # Should load successfully, ignoring unknown fields
        assert config.enable_editor_pipeline is True
        # Unknown fields should not be present
        assert not hasattr(config, 'unknown_field')
    
    @pytest.mark.edge_case
    def test_save_config_readonly_directory(self, temp_dir):
        """Test handling of readonly directory during save"""
        manager = ConfigManager(temp_dir)
        config = ImportConfig()
        
        # Create a readonly directory (this is platform-dependent)
        readonly_dir = temp_dir / "readonly"
        readonly_dir.mkdir()
        
        try:
            # On Windows, we can't easily make directories readonly
            # So we'll just test that the method handles exceptions
            readonly_file = readonly_dir / "config.yaml"
            
            # This should handle any permission errors gracefully
            manager.save_config(config, readonly_file)
        except PermissionError:
            # Expected on some platforms
            pass