from pathlib import Path

from src.config import ImportConfig, ConfigManager


def test_validate_llm_prompt_template_missing(tmp_path):
    cfg = ImportConfig()
    cfg.enable_llm_categorization = True
    cfg.llm_prompt_template_path = str(tmp_path / "missing.txt")
    warnings = ConfigManager().validate_config(cfg)
    assert any("llm_prompt_template_path" in w for w in warnings)


def test_validate_llm_tags_bounds():
    cfg = ImportConfig()
    cfg.enable_llm_categorization = True
    cfg.llm_tags_max_count = -1
    w = ConfigManager().validate_config(cfg)
    assert any("llm_tags_max_count" in x for x in w)

    cfg.llm_tags_max_count = 2
    cfg.llm_tags_min_count = -1
    w = ConfigManager().validate_config(cfg)
    assert any("llm_tags_min_count must be >= 0" in x for x in w)

    cfg.llm_tags_min_count = 3
    cfg.llm_tags_max_count = 2
    w = ConfigManager().validate_config(cfg)
    assert any("llm_tags_min_count must be <= llm_tags_max_count" in x for x in w)


def test_default_undecided_policy_is_suggest():
    cfg = ImportConfig()
    assert getattr(cfg, 'undecided_policy') == 'suggest'


def test_create_sample_config_includes_new_keys(tmp_path):
    cm = ConfigManager(config_dir=tmp_path)
    out = tmp_path / "sample_config.yaml"
    cm.create_sample_config(out)
    text = out.read_text(encoding='utf-8')
    assert 'llm_prompt_version' in text
    assert 'llm_prompt_template_path' in text
    assert 'llm_tags_max_count' in text
    assert 'llm_tags_min_count' in text