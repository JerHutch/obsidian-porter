import os
import json
import tempfile
from pathlib import Path

import pytest

from src.config import ImportConfig
from src.pipelines.category_classifier import CategoryClassifier, _ClassificationResult


def make_config(**overrides):
    cfg = ImportConfig()
    cfg.enable_llm_categorization = True
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def test_freeform_suggestions_kept(monkeypatch):
    cfg = make_config(undecided_policy='suggest', suggestions_count=2)
    clf = CategoryClassifier(config=cfg)

    def fake_provider(text, categories):
        return _ClassificationResult(category_slug=None, confidence=0.4, reasons='', suggestions=['work', 'finance', 'music'], tags=[])

    monkeypatch.setattr(clf, "_classify_with_provider", fake_provider)

    _, meta = clf.process("some text", {}, {"filename": "n.txt"})
    assert meta.get('category') is None
    assert meta.get('_category_suggestions') == ['work', 'finance']


def test_llm_tags_normalization_and_cap(monkeypatch):
    cfg = make_config(llm_suggest_tags=True, llm_tags_max_count=5)
    cfg.llm_cache_enabled = False
    clf = CategoryClassifier(config=cfg)

    def fake_provider(text, categories):
        tags = ["Home Improvement", "to_do", "HVAC", "SQL/DB", "Long Tag Name!!", "extra"]
        return _ClassificationResult(category_slug=None, confidence=0.0, reasons='', suggestions=[], tags=tags)

    monkeypatch.setattr(clf, "_classify_with_provider", fake_provider)

    _, meta = clf.process("text", {}, {"filename": "n.txt"})
    assert meta['llm_tags'] == ["home-improvement", "to-do", "hvac", "sql-db", "long-tag-name"]


def test_cache_key_changes_with_prompt_version(monkeypatch):
    cfg = make_config(llm_prompt_version="v1")
    clf1 = CategoryClassifier(config=cfg)
    k1 = clf1._cache_key("text", ["house", "other"])

    cfg.llm_prompt_version = "v2"
    clf2 = CategoryClassifier(config=cfg)
    k2 = clf2._cache_key("text", ["house", "other"])

    assert k1 != k2


def test_cache_key_changes_with_template_content(tmp_path, monkeypatch):
    # Write a custom template and ensure changing its contents affects the key
    tfile = tmp_path / "tmpl.txt"
    tfile.write_text("Version: {{llm_prompt_version}}\n{{text}}", encoding='utf-8')

    cfg = make_config(llm_prompt_template_path=str(tfile), llm_prompt_version="v1")
    clf1 = CategoryClassifier(config=cfg)
    k1 = clf1._cache_key("text", ["other"]) 

    # Change template
    tfile.write_text("DIFF: {{llm_prompt_version}}\n{{text}}", encoding='utf-8')
    clf2 = CategoryClassifier(config=cfg)
    k2 = clf2._cache_key("text", ["other"]) 

    assert k1 != k2


def test_code_fence_stripping(monkeypatch):
    cfg = make_config()
    cfg.llm_cache_enabled = False
    clf = CategoryClassifier(config=cfg)

    def fake_completion(**kwargs):
        content = """```json
{"category_slug":"house","confidence":0.9,"reasons":"","suggestions":[],"tags":[]}
```"""
        return {"choices": [{"message": {"content": content}}]}

    # Patch litellm.completion used inside classifier
    monkeypatch.setattr("src.pipelines.category_classifier.llm_completion", fake_completion)

    _, meta = clf.process("text", {}, {"filename": "n.txt"})
    assert meta.get('category') == 'house'


def test_provider_env_mapping(monkeypatch):
    cfg = make_config(llm_api_keys={'openai': 'CUSTOM_OPENAI_KEY'})
    cfg.llm_cache_enabled = False
    clf = CategoryClassifier(config=cfg)

    def fake_completion(**kwargs):
        return {"choices": [{"message": {"content": json.dumps({
            "category_slug": "other", "confidence": 0.1, "reasons": "", "suggestions": [], "tags": []
        })}}]}

    # Prepare env
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    os.environ['CUSTOM_OPENAI_KEY'] = 'testkey'

    monkeypatch.setattr("src.pipelines.category_classifier.llm_completion", fake_completion)

    _, meta = clf.process("text", {}, {"filename": "n.txt"})
    assert os.environ.get('OPENAI_API_KEY') == 'testkey'


def test_provider_exception_fallback(monkeypatch):
    cfg = make_config(undecided_policy='suggest')
    cfg.llm_cache_enabled = False
    clf = CategoryClassifier(config=cfg)

    def boom(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("src.pipelines.category_classifier.llm_completion", boom)

    _, meta = clf.process("text", {}, {"filename": "n.txt"})
    # No crash, suggestions absent, and no category assigned under suggest policy
    assert 'category' not in meta