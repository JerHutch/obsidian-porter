"""
Pytest configuration and shared fixtures for SimpleNote to Obsidian Importer tests.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

import pytest

from src.config import ImportConfig, ConfigManager
from src.interfaces import MockFileSystem


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_notes_dir():
    """Path to sample notes fixtures."""
    return Path(__file__).parent / "fixtures" / "sample_notes"


@pytest.fixture
def sample_json_dir():
    """Path to sample JSON fixtures.""" 
    return Path(__file__).parent / "fixtures" / "sample_json"


@pytest.fixture
def basic_metadata_json(sample_json_dir):
    """Load basic metadata JSON fixture."""
    with open(sample_json_dir / "basic_metadata.json") as f:
        return json.load(f)


@pytest.fixture
def complex_metadata_json(sample_json_dir):
    """Load complex metadata JSON fixture."""
    with open(sample_json_dir / "complex_metadata.json") as f:
        return json.load(f)


@pytest.fixture 
def edge_cases_json(sample_json_dir):
    """Load edge cases JSON fixture."""
    with open(sample_json_dir / "edge_cases.json") as f:
        return json.load(f)


@pytest.fixture
def invalid_metadata_json(sample_json_dir):
    """Load invalid metadata JSON fixture."""
    with open(sample_json_dir / "invalid_metadata.json") as f:
        return json.load(f)


@pytest.fixture
def simple_note_content(sample_notes_dir):
    """Load simple note text content."""
    with open(sample_notes_dir / "simple_note_1.txt", encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def complex_note_content(sample_notes_dir):
    """Load complex note text content."""
    with open(sample_notes_dir / "complex_note_with_tags.txt", encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def special_chars_content(sample_notes_dir):
    """Load special characters note content."""
    with open(sample_notes_dir / "note_with_special_chars.txt", encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def minimal_config():
    """Create minimal configuration for testing."""
    return ImportConfig(
        editor_enabled=False,
        auto_tagging_enabled=False,
        folder_organization_enabled=False,
        content_transformation_enabled=False
    )


@pytest.fixture
def full_config():
    """Create full configuration with all features enabled."""
    return ImportConfig(
        editor_enabled=True,
        auto_tagging_enabled=True,
        folder_organization_enabled=True,
        content_transformation_enabled=True,
        auto_tag_patterns={
            "project": ["project", "sprint", "planning"],
            "meeting": ["meeting", "agenda", "notes"],
            "development": ["code", "programming", "development"]
        },
        folder_rules={
            "Projects": ["project", "planning"],
            "Meetings": ["meeting", "agenda"], 
            "Development": ["code", "programming"]
        }
    )


@pytest.fixture
def mock_file_system():
    """Mock file system interface for testing."""
    return MockFileSystem()

@pytest.fixture
def mock_file_system_legacy():
    """Legacy mock file system interface for existing tests."""
    mock_fs = Mock()
    mock_fs.exists.return_value = True
    mock_fs.read_text.return_value = "Mock file content"
    mock_fs.write_text.return_value = None
    mock_fs.mkdir.return_value = None
    mock_fs.glob.return_value = []
    return mock_fs


@pytest.fixture
def sample_note_data():
    """Sample note data structure for testing."""
    return {
        "id": "test-id-001",
        "title": "Test Note Title",
        "content": "This is test note content\nwith multiple lines.",
        "created": "2024-01-01T10:00:00.000Z",
        "modified": "2024-01-01T10:30:00.000Z",
        "tags": ["test", "sample"],
        "markdown": False,
        "pinned": False
    }


@pytest.fixture
def sample_metadata():
    """Sample metadata dictionary for testing."""
    return {
        "test-note-1.txt": {
            "id": "test-id-001",
            "created": "2024-01-01T10:00:00.000Z",
            "modified": "2024-01-01T10:30:00.000Z",
            "tags": ["test"],
            "markdown": False,
            "pinned": False
        }
    }


@pytest.fixture
def expected_yaml_frontmatter():
    """Expected YAML frontmatter for test notes."""
    return """---
title: Test Note Title
created: 2024-01-01T10:00:00.000Z
modified: 2024-01-01T10:30:00.000Z
source: simplenote
original_id: test-id-001
tags:
  - test
  - sample
markdown: false
pinned: false
---

This is test note content
with multiple lines."""