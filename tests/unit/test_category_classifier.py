import pytest

from src.config import ImportConfig
from src.pipelines.category_classifier import CategoryClassifier, _ClassificationResult
from src.pipelines.tag_injector import TagInjector
from src.pipelines.folder_organizer import FolderOrganizer


def make_config(**overrides):
    cfg = ImportConfig()
    # Enable LLM categorization by default for these tests
    cfg.enable_llm_categorization = True
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def test_category_classifier_confident_assignment(monkeypatch):
    cfg = make_config()
    clf = CategoryClassifier(config=cfg)

    def fake_provider(text, categories):
        return _ClassificationResult(category_slug='house', confidence=0.95, reasons='home', suggestions=[])

    monkeypatch.setattr(clf, "_classify_with_provider", fake_provider)

    content = "Fixing the water heater and scheduling HVAC maintenance."
    metadata = {}
    context = {"filename": "note.txt"}

    out_content, out_meta = clf.process(content, metadata, context)

    assert out_meta.get('category') == 'house'
    assert out_meta.get('_category_confidence') == pytest.approx(0.95, rel=1e-6)


def test_category_classifier_low_confidence_other_policy(monkeypatch):
    cfg = make_config(llm_min_confidence=0.8, undecided_policy='other')
    clf = CategoryClassifier(config=cfg)

    def fake_provider(text, categories):
        return _ClassificationResult(category_slug='music', confidence=0.5, reasons='unsure', suggestions=['music'])

    monkeypatch.setattr(clf, "_classify_with_provider", fake_provider)

    content = "Short note"
    metadata = {}
    context = {"filename": "note.txt"}

    _, out_meta = clf.process(content, metadata, context)

    assert out_meta.get('category') == 'other'


def test_category_classifier_suggest_policy(monkeypatch):
    cfg = make_config(llm_min_confidence=0.9, undecided_policy='suggest', suggestions_count=2)
    clf = CategoryClassifier(config=cfg)

    def fake_provider(text, categories):
        return _ClassificationResult(category_slug=None, confidence=0.4, reasons='ambiguous', suggestions=['house', 'recipes', 'gaming'])

    monkeypatch.setattr(clf, "_classify_with_provider", fake_provider)

    _, out_meta = clf.process("text", {}, {"filename": "n.txt"})

    # category should be unset, suggestions present and capped
    assert 'category' not in out_meta
    assert out_meta.get('_category_suggestions') == ['house', 'recipes']


def test_category_classifier_truncation(monkeypatch):
    cfg = make_config(llm_head_chars=10, llm_tail_chars=5)
    cfg.llm_cache_enabled = False  # ensure provider is called
    clf = CategoryClassifier(config=cfg)

    captured = {}

    def fake_provider(text, categories):
        captured['text'] = text
        return _ClassificationResult(category_slug=None, confidence=0.0, reasons='', suggestions=[], undecided=True)

    monkeypatch.setattr(clf, "_classify_with_provider", fake_provider)

    content = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 26 chars
    clf.process(content, {}, {"filename": "n.txt"})

    expected = content[:10] + "\n\n...\n\n" + content[-5:]
    assert captured['text'] == expected


def test_tag_injector_propagates_category_tag():
    injector = TagInjector(tag_rules={}, propagate_category_tag=True)
    content = "- item 1\n- item 2\n- item 3\n- item 4"  # triggers 'lists' maybe
    metadata = {"tags": ["foo"], "category": "gaming"}
    context = {"filename": "g.txt"}

    _, out_meta = injector.process(content, metadata, context)

    assert 'gaming' in out_meta.get('tags', [])


def test_folder_organizer_prefers_category():
    org = FolderOrganizer()
    content = "some text"
    metadata = {"category": "house", "tags": ["music"]}
    context = {"filename": "x.txt"}

    _, out_meta = org.process(content, metadata, context)

    assert out_meta.get('_folder_path') == 'house'