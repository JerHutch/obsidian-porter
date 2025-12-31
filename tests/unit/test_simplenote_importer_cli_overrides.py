import os
from pathlib import Path

import pytest

from src.simplenote_importer import main, SimpleNoteImporter


def test_cli_overrides_new_llm_flags(monkeypatch, tmp_path, capsys):
    notes = tmp_path / "notes"
    notes.mkdir()

    captured = {}

    def fake_init(self, notes_directory, json_path, output_directory, config, file_system=None):
        captured['config'] = config

    def fake_run(self):
        return True

    monkeypatch.setattr(SimpleNoteImporter, "__init__", fake_init, raising=False)
    monkeypatch.setattr(SimpleNoteImporter, "run", fake_run, raising=False)
    monkeypatch.setattr("sys.exit", lambda code=0: None)

    argv = [
        "import.py", "--notes", str(notes), "--smart",
        "--enable-llm", "--llm-provider", "openai",
        "--llm-prompt-template", "config/prompts/default_classifier_prompt.txt",
        "--llm-prompt-version", "vX",
        "--llm-allow-freeform-suggestions",
        "--llm-suggest-tags",
        "--llm-tags-max", "7",
        "--llm-tags-min", "1",
        "--llm-suggestions-count", "4",
    ]

    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setattr("sys.argv", argv)

    main()

    cfg = captured['config']
    assert cfg.enable_llm_categorization is True
    assert cfg.llm_prompt_template_path.endswith("default_classifier_prompt.txt")
    assert cfg.llm_prompt_version == "vX"
    assert cfg.llm_allow_freeform_suggestions is True
    assert cfg.llm_suggest_tags is True
    assert cfg.llm_tags_max_count == 7
    assert cfg.llm_tags_min_count == 1
    assert cfg.suggestions_count == 4


def test_cli_sets_default_model_for_openai(monkeypatch, tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()

    captured = {}

    def fake_init(self, notes_directory, json_path, output_directory, config, file_system=None):
        captured['config'] = config

    def fake_run(self):
        return True

    monkeypatch.setattr(SimpleNoteImporter, "__init__", fake_init, raising=False)
    monkeypatch.setattr(SimpleNoteImporter, "run", fake_run, raising=False)
    monkeypatch.setattr("sys.exit", lambda code=0: None)

    argv = [
        "import.py", "--notes", str(notes), "--smart",
        "--enable-llm", "--llm-provider", "openai",
    ]

    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setattr("sys.argv", argv)

    main()

    cfg = captured['config']
    assert cfg.llm_model == 'gpt-4o-mini'


def test_cli_clear_llm_cache(monkeypatch, tmp_path, capsys):
    notes = tmp_path / "notes"
    notes.mkdir()

    cache_dir = Path('.cache')
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / 'llm_category.jsonl'
    cache_file.write_text('x', encoding='utf-8')

    def fake_init(self, notes_directory, json_path, output_directory, config, file_system=None):
        pass

    def fake_run(self):
        return True

    monkeypatch.setattr(SimpleNoteImporter, "__init__", fake_init, raising=False)
    monkeypatch.setattr(SimpleNoteImporter, "run", fake_run, raising=False)
    monkeypatch.setattr("sys.exit", lambda code=0: None)

    argv = [
        "import.py", "--notes", str(notes), "--smart",
        "--clear-llm-cache"
    ]

    monkeypatch.setattr("sys.argv", argv)

    main()

    out = capsys.readouterr().out
    assert "Cleared LLM cache" in out or "No LLM cache to clear" in out
    # File should be removed if it existed
    assert not cache_file.exists()