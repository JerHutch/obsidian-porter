import pytest
from pathlib import Path

from src.config import ImportConfig, ConfigManager


def test_sample_config_full_loads_without_errors():
    cfg_path = Path("config/sample_config_full.yaml")
    assert cfg_path.exists(), "config/sample_config_full.yaml should exist"

    cfg = ImportConfig.load_from_file(cfg_path)

    # Phase 2 toggles
    assert cfg.enable_editor_pipeline is True
    assert cfg.enable_auto_tagging is True
    assert cfg.enable_folder_organization is True
    assert cfg.enable_content_transformation is True

    # LLM basics
    assert cfg.enable_llm_categorization is False
    assert cfg.llm_provider in ["openai", "anthropic", "ollama", "vertex", "groq"]
    assert isinstance(cfg.llm_timeout_sec, int) and cfg.llm_timeout_sec > 0
    assert isinstance(cfg.llm_concurrency, int) and cfg.llm_concurrency >= 1
    assert isinstance(cfg.llm_min_confidence, float) and 0.0 <= cfg.llm_min_confidence <= 1.0

    # Categories must include 'other' and be unique
    slugs = [c.get("slug") for c in (cfg.categories or [])]
    assert "other" in slugs
    assert len(slugs) == len(set(slugs))

    # Cache path provided
    assert isinstance(cfg.llm_cache_path, str) and len(cfg.llm_cache_path) > 0

    # Tagging config types
    assert isinstance(cfg.custom_tag_rules, dict)
    assert (cfg.tag_whitelist is None) or isinstance(cfg.tag_whitelist, list)
    assert isinstance(cfg.tag_blacklist, list)

    # Folder rules
    assert isinstance(cfg.custom_folder_rules, dict)

    # Splitting fields
    assert isinstance(cfg.split_header_level, int)
    assert isinstance(cfg.preserve_main_header, bool)
    assert isinstance(cfg.split_notes_patterns, list)
    assert isinstance(cfg.split_enabled_tags, list)

    # Validate configuration
    warnings = ConfigManager().validate_config(cfg)
    assert not warnings, f"Unexpected configuration warnings: {warnings}"


def test_config_manager_save_and_load_roundtrip(tmp_path):
    # Create a config, save it, and load it back
    cfg = ImportConfig()
    cfg.enable_llm_categorization = True
    cfg.llm_provider = "openai"
    cfg.llm_model = "gpt-4o-mini"
    cfg.llm_min_confidence = 0.7

    out = tmp_path / "roundtrip.yaml"
    cfg.save_to_file(out)

    loaded = ImportConfig.load_from_file(out)
    assert loaded.enable_llm_categorization is True
    assert loaded.llm_provider == "openai"
    assert loaded.llm_model == "gpt-4o-mini"
    assert loaded.llm_min_confidence == pytest.approx(0.7, rel=1e-6)
