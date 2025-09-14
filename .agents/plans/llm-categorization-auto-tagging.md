# Phase 3: LLM-based Note Categorization and Auto-Tagging Plan

1) Goals and success criteria
- Replace regex-driven category detection with an LLM classifier that assigns exactly one primary category from a configurable list per note, with optional secondary suggestions.
- If undecided or low confidence, assign Other (or suggest candidates, based on config).
- The chosen category must influence the rest of the pipeline: tags and folder organization.
- Support multiple LLM providers with per-provider API key and model selection, one provider/model per run.
- Deterministic, fast, offline-safe tests (mocked LLM). Maintain backward compatibility when LLM is disabled.
- Success metrics:
  - Measurable reduction in misclassifications on sample dataset versus current regex TagInjector rules.
  - Zero crashes across the pipeline with LLM enabled/disabled.
  - Tests >90% coverage on new core logic (LLM client abstraction, CategoryClassifier, config wiring).
  - No network in tests; all LLM calls mocked.

2) Scope and non-goals
- In scope:
  - New CategoryClassifier processor (src/pipelines/category_classifier.py).
  - Provider-agnostic LLM client abstraction (src/llm/*).
  - Config/CLI options and validation.
  - Local cache and basic rate limiting/backoff with optional concurrency.
  - Integration with FolderOrganizer and TagInjector.
  - Documentation updates and a comprehensive test suite (unit + integration).
- Out of scope:
  - Fine-tuned/custom models, RAG, embeddings.
  - Multi-label final categories (only single primary label; suggestions optional).
  - Automatic model selection.
  - Complex analytics or telemetry.

3) Architecture changes
- New processor: src/pipelines/category_classifier.py
  - Role: Runs first in EditorPipeline. Consumes note content, outputs same content plus metadata updates.
  - Behavior:
    - Determine exactly one primary category from config.categories by slug.
    - When confidence below threshold or ambiguous:
      - If undecided_policy == "other": set metadata['category'] = 'other'.
      - If undecided_policy == "suggest": leave metadata['category'] unset and attach metadata['_category_suggestions'] = [slugs] (up to suggestions_count).
    - Always attach diagnostics:
      - metadata['_category_confidence'] = float 0..1
      - metadata['_category_reasoning'] = brief string (not written to YAML frontmatter by default)
      - metadata['_category_provider'] = provider string and metadata['_category_model'] = model string
    - Tag propagation:
      - If propagate_category_tag is True and a category is chosen, ensure the slug is present in metadata['tags'].
    - Content trimming to stay within model limits:
      - Trim to first N and last M characters; configurable.
      - Default total cap: 3000 chars (head 2500, tail 500).
  - Testability:
    - Accept an injected LLM client (protocol) for unit tests.
    - Accept a file system interface for caching (reuse src.interfaces.FileSystemInterface).
- New LLM abstraction (no hard deps on core path)
  - src/llm/client_base.py
    - Define protocol interface LLMClient with:
      - classify_note(note_text: str, categories: list[Category], prompt_config: PromptConfig) -> ClassificationResult
    - dataclasses: Category(name, slug, description), ClassificationResult(category_slug: Optional[str], confidence: float, reasons: str, suggestions: list[str], undecided: bool)
    - PromptConfig includes: allowed_slugs, undecided_token ("other"), max_chars, head_chars, tail_chars, prompt_version, min_confidence.
  - src/llm/providers/openai_client.py (implemented)
    - Lazy import openai SDK or use OpenAI-compatible HTTP endpoint via llm_base_url.
    - Reads API key from environment variable specified by config.llm_api_keys['openai'] or default OPENAI_API_KEY.
  - src/llm/providers/ollama_client.py (implemented via OpenAI-compatible API)
    - Uses llm_base_url (e.g., http://localhost:11434/v1) and token if required.
  - src/llm/providers/anthropic_client.py (stub or implemented)
    - Optional; read ANTHROPIC_API_KEY; lazy import anthropic SDK if present.
  - src/llm/prompting.py
    - Build system/user messages and strict JSON schema. Model must return JSON object:
      {
        "category_slug": "one-of-allowed-or-other",
        "confidence": 0.0-1.0,
        "reasons": "brief explanation",
        "suggestions": ["slug1", "slug2", ...]
      }
    - Include explicit list of allowed slugs and the fallback "other".
    - Include guardrails for short or empty notes to return "other" with low confidence and brief reason.
    - Include prompt_version constant used in cache keys and parsing.
- Config changes (src/config.py)
  - Add fields to ImportConfig (defaults shown):
    - enable_llm_categorization: bool = False
    - llm_provider: str = "openai"  # allowed: openai, anthropic, ollama, vertex, groq
    - llm_model: Optional[str] = None  # e.g., "gpt-4o-mini", "claude-3-haiku", "llama3.1:8b"
    - llm_api_keys: Dict[str, str] = {}  # mapping provider -> ENV VAR NAME (no secrets in files)
    - llm_base_url: Optional[str] = None  # for OpenAI-compatible endpoints (Ollama, Groq, custom gateways)
    - llm_timeout_sec: int = 30
    - llm_max_retries: int = 2
    - llm_concurrency: int = 4
    - llm_cache_enabled: bool = True
    - llm_cache_path: str = ".cache/llm_category.jsonl"
    - categories: List[Dict[str, str]] = default list below (name, slug, description)
    - undecided_policy: str = "other"  # "other" or "suggest"
    - suggestions_count: int = 3
    - propagate_category_tag: bool = True
    - llm_min_confidence: float = 0.6  # threshold for “confident” primary assignment (to minimize false positives)
    - llm_head_chars: int = 2500
    - llm_tail_chars: int = 500
  - ConfigManager.create_sample_config:
    - Add a commented LLM section with placeholders and notes about ENV VAR usage.
  - ConfigManager.validate_config:
    - Validate llm_provider is in allowlist.
    - Validate categories slugs unique and include "other".
    - Validate numeric ranges (timeouts, retries, concurrency >=1, min_confidence in [0,1]).
    - Warn if LLM is enabled but no API key env var configured or found.
- Editor pipeline wiring (src/simplenote_importer.py::_setup_editor_pipeline)
  - Insert CategoryClassifier before TagInjector and FolderOrganizer when config.enable_llm_categorization is True.
  - Order becomes:
    1) CategoryClassifier (new)
    2) TagInjector (existing)
    3) FolderOrganizer (existing)
    4) ContentTransformer (existing)
    5) NoteSplitter (existing if enabled)
  - Pass ImportConfig to CategoryClassifier for runtime parameters.
- FolderOrganizer (src/pipelines/folder_organizer.py)
  - Prefer metadata['category'] to determine folder via a mapping:
    - If category present, map slug -> folder path using existing custom_folder_rules or a new implicit mapping (e.g., same as slug).
    - If absent, fallback to current heuristics based on tags/content.
  - Continue honoring existing config options (organize_by_folder, folder_structure).
- TagInjector (src/pipelines/tag_injector.py)
  - If propagate_category_tag and metadata['category'] set, ensure it appears in metadata['tags'].
  - Continue to apply regex-based auto-tagging per existing rules, but category tag should remain.
- ObsidianFormatter (unchanged)
  - Continues to produce YAML frontmatter. Folder path comes from FolderOrganizer via metadata['_folder_path'] as today.

4) Providers and prompt strategy
- Initial providers:
  - OpenAI: implemented first. Default provider.
  - Ollama: implemented via OpenAI-compatible local endpoint; allows fully local classification.
  - Anthropic: stub or implemented next (optional for initial PR).
- Prompting:
  - System prompt: define role, constraints, and JSON-only output rule.
  - User prompt: include:
    - Allowed category slugs (plus “other”).
    - Category descriptions.
    - Truncated note text (first head_chars and last tail_chars).
    - Requirements:
      - Choose exactly one category slug from list or "other".
      - Provide confidence 0..1 and reasons (brief).
      - Provide up to N suggestions (slugs) if uncertain.
    - Guardrails: If note is too short/empty/off-topic, return "other" with low confidence.
  - Strict JSON parsing:
    - Use defensive parsing with fallback to undecided policy if parsing fails.
- Truncation:
  - Default: total 3000 chars (head 2500, tail 500), configurable in config.
  - Ensures predictable token usage and performance.

5) Initial categories (config defaults)
- Defaults for ImportConfig.categories (list of objects with name, slug, description):
  - { name: "Cocktails", slug: "cocktails", description: "Cocktail recipes, mixed drinks, ingredients, techniques." }
  - { name: "Recipes", slug: "recipes", description: "Food recipes, ingredients, cooking instructions." }
  - { name: "Gaming", slug: "gaming", description: "Video games, gameplay notes, walkthroughs, strategies." }
  - { name: "Music", slug: "music", description: "Music notes, artists, songs, albums, playlists." }
  - { name: "Track lists", slug: "track-lists", description: "Tracklists, DJ sets, setlists, ordered lists of tracks." }
  - { name: "House", slug: "house", description: "Clarify: house music vs home/household notes (see Open Questions)." }
  - { name: "Role-playing games", slug: "role-playing-games", description: "Tabletop RPGs, characters, campaigns, rules." }
  - { name: "Cisco", slug: "cisco", description: "Networking/Cisco notes, configs, commands." }
  - { name: "Other", slug: "other", description: "Fallback category for low-confidence or uncategorized notes." }

6) Caching and rate limiting
- Caching:
  - JSONL file at .cache/llm_category.jsonl (config.llm_cache_path).
  - Key: SHA256 of (note_text_trimmed + sorted_category_slugs + provider + model + prompt_version).
  - Value: ClassificationResult JSON, plus metadata for debugging (timestamp, durations).
  - Implemented inside CategoryClassifier using FileSystemInterface for IO.
- Rate limiting / retries / concurrency:
  - Exponential backoff on HTTP 429/5xx up to llm_max_retries.
  - Basic concurrency with asyncio.Semaphore(llm_concurrency).
  - Provide serial mode by setting llm_concurrency=1.
  - NOTE: The current SimpleNoteImporter processes notes sequentially. Concurrency support will be implemented inside the LLM client and CategoryClassifier to enable future batch mode; initial wire-up can remain sequential for the first PR.

7) CLI and configuration UX
- import.py (entrypoint):
  - Add flags:
    - --enable-llm (bool)
    - --llm-provider openai|anthropic|ollama|vertex|groq
    - --llm-model MODEL_NAME
    - --llm-timeout SECONDS
    - --llm-concurrency INT
    - --llm-base-url URL
  - Respect --config overrides and merge with CLI (CLI takes precedence).
  - Categories are specified in YAML config (not via CLI).
- ConfigManager.create_sample_config:
  - Include a commented LLM section:
    - enable_llm_categorization: false
    - llm_provider: openai
    - llm_model: gpt-4o-mini
    - llm_api_keys:
        openai: OPENAI_API_KEY
        anthropic: ANTHROPIC_API_KEY
        ollama: OLLAMA_API_KEY  # optional; local usually does not require
    - llm_base_url: http://localhost:11434/v1  # for Ollama
    - llm_timeout_sec: 30
    - llm_max_retries: 2
    - llm_concurrency: 4
    - llm_cache_enabled: true
    - llm_cache_path: .cache/llm_category.jsonl
    - llm_min_confidence: 0.6
    - llm_head_chars: 2500
    - llm_tail_chars: 500
    - undecided_policy: other  # other | suggest
    - suggestions_count: 3
    - propagate_category_tag: true
    - categories:
        - { name: Cocktails, slug: cocktails, description: "Cocktail recipes..." }
        - ...
- README/CLAUDE.md:
  - Document enabling LLM, provider/model selection, environment variable setup.
  - Privacy note about sending content to third-party providers if not using local Ollama.
  - macOS zsh quickstart with .venv activation.

8) Testing strategy (pytest)
- Unit tests (tests/unit):
  - test_category_classifier.py:
    - confident classification -> sets metadata['category'] and adds tag when propagate enabled.
    - undecided -> policy "other" assigns other; policy "suggest" leaves unset and sets _category_suggestions.
    - truncation logic: given long text, ensures only head/tail are used in prompt.
    - cache: hit vs miss behavior; ensure no provider call on hit.
    - low confidence -> triggers undecided policy; threshold enforced via llm_min_confidence.
  - test_llm_prompting.py:
    - prompt builder includes all slugs, descriptions, and truncation boundaries.
    - JSON parsing robustness with minor deviations; falls back safely.
  - test_llm_provider_selection.py:
    - Factory chooses provider client.
    - Missing API key env var yields clear error (unless provider is local with base_url).
  - test_folder_organizer_integration.py:
    - With metadata['category'], folder mapping prefers category.
  - test_config_validation.py:
    - Validates provider, categories, and numeric ranges. Backward compatibility with defaults off.
- Integration tests (tests/integration):
  - test_pipeline_llm_enabled_mocked.py:
    - Monkeypatch CategoryClassifier to return fixed results for multiple notes.
    - Verify tags and folders reflect chosen category.
  - test_pipeline_llm_disabled_backcompat.py:
    - Ensure behavior is identical to current pipeline when enable_llm_categorization=False.
- Notes:
  - No network calls. Inject Mock LLMClient into CategoryClassifier.
  - Keep tests deterministic and fast; leverage FileSystemInterface for cache IO.

9) Security, privacy, and failure handling
- Secrets:
  - Never write API keys to disk. Read from environment variables only (names configured in llm_api_keys).
  - If API key missing at runtime for remote providers, fail with actionable error pointing to env var name.
- Providers allowlist:
  - Validate llm_provider against known list to avoid accidental remote calls.
- Failures:
  - On API or parsing failure, default to undecided policy (no crash).
  - Add try/except around provider calls and robust JSON parsing fallback.
- Optional redaction:
  - Leave a hook to redact long URLs or suspected secrets before sending to LLM (future enhancement).
- .gitignore:
  - Add .cache/ to .gitignore so caches are not committed.

10) Migration and backward compatibility
- If enable_llm_categorization is False (default), behavior is unchanged.
- Existing custom_tag_rules and folder rules remain in effect.
- FolderOrganizer now prefers a chosen metadata['category'] if present; otherwise uses existing heuristics.
- TagInjector continues to operate; category tag propagation is additive and can be disabled via propagate_category_tag.

11) Delivery checklist
- Branch:
  - git checkout -b feature/llm-categorization
- Code:
  - Add new modules:
    - src/pipelines/category_classifier.py
    - src/llm/client_base.py
    - src/llm/prompting.py
    - src/llm/providers/openai_client.py
    - src/llm/providers/ollama_client.py
    - src/llm/providers/anthropic_client.py (stub/next)
  - Update existing:
    - src/config.py (new fields, load/save, defaults)
    - src/simplenote_importer.py::_setup_editor_pipeline (insert CategoryClassifier first)
    - src/pipelines/folder_organizer.py (prefer category)
    - src/pipelines/tag_injector.py (ensure category tag if configured)
    - ConfigManager.create_sample_config() (LLM section)
    - ConfigManager.validate_config() (new validations)
    - import.py (CLI flags)
  - Tests:
    - tests/unit/*.py (as above)
    - tests/integration/*.py (as above)
  - Docs:
    - README.md and CLAUDE.md updated to explain LLM usage, env vars, privacy.
  - Repo:
    - .gitignore: add .cache/
- Run tests:
  - source .venv/bin/activate
  - python -m pytest -v
  - python -m pytest --cov=src --cov-report=html
- Manual sanity test (no network):
  - Run importer with enable_llm_categorization=False to verify back-compat.
- Manual test with local Ollama (optional):
  - Start Ollama, set llm_base_url and enable LLM; run on small sample.

12) Open questions for the user
- Providers:
  - Confirm initial providers: OpenAI and local (Ollama) for first iteration; add Anthropic now or in a follow-up?
  - Default models per provider:
    - openai: gpt-4o-mini (or gpt-4o-mini-2024-07-18)?
    - anthropic: claude-3-haiku?
    - ollama: llama3.1:8b?
- Category semantics:
  - Is “House” intended as house music or household/home-related notes?
  - Is “Cisco” intended to remain a top-level category?
- Label policy:
  - Confirm strictly single primary category only; are secondary suggestions acceptable to store in metadata (not in frontmatter)?
- Performance:
  - Acceptable latency per note? Target concurrency level?
  - Is a pre-pass batch classification step acceptable in the future to parallelize LLM calls?
- Privacy:
  - Any constraints requiring local-only mode sometimes?
  - Should we parse-and-redact potential secrets/URLs before sending to cloud LLMs?
- Repo hygiene:
  - Is storing the cache at .cache/ acceptable? Add to .gitignore?
- Config extras:
  - Is llm_min_confidence at 0.6 acceptable as default? Adjust preferred default?

13) Implementation estimate
- Core implementation: 1–2 days
  - CategoryClassifier, LLM abstraction, OpenAI + Ollama clients, config wiring, pipeline integration.
- Tests and documentation: ~1 day
  - Unit + integration tests, README/CLAUDE updates, sample config.
- Total: ~2–3 days elapsed including review.

Appendix A: Code path references for changes
- New files:
  - src/pipelines/category_classifier.py
  - src/llm/client_base.py
  - src/llm/prompting.py
  - src/llm/providers/openai_client.py
  - src/llm/providers/ollama_client.py
  - src/llm/providers/anthropic_client.py (stub)
- Modified files:
  - src/config.py (ImportConfig fields; ConfigManager.create_sample_config; ConfigManager.validate_config)
  - src/simplenote_importer.py::_setup_editor_pipeline (insert CategoryClassifier first)
  - src/pipelines/folder_organizer.py (prefer metadata['category'])
  - src/pipelines/tag_injector.py (ensure category tag if configured)
  - import.py (CLI flags)
  - .gitignore (add .cache/)
- Tests:
  - tests/unit/test_category_classifier.py
  - tests/unit/test_llm_prompting.py
  - tests/unit/test_llm_provider_selection.py
  - tests/unit/test_folder_organizer_integration.py
  - tests/unit/test_config_validation.py
  - tests/integration/test_pipeline_llm_enabled_mocked.py
  - tests/integration/test_pipeline_llm_disabled_backcompat.py

Appendix B: Minimal pseudo-interfaces (for reference)

src/llm/client_base.py
------------------------------------------------
from dataclasses import dataclass
from typing import List, Optional, Protocol

@dataclass
class Category:
    name: str
    slug: str
    description: str

@dataclass
class ClassificationResult:
    category_slug: Optional[str]
    confidence: float
    reasons: str
    suggestions: List[str]
    undecided: bool = False

@dataclass
class PromptConfig:
    allowed_slugs: List[str]
    undecided_token: str
    prompt_version: str
    max_chars: int
    head_chars: int
    tail_chars: int
    min_confidence: float

class LLMClient(Protocol):
    def classify_note(self, note_text: str, categories: List[Category], config: PromptConfig) -> ClassificationResult: ...