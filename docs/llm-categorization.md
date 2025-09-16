# LLM-based Note Categorization

This document describes the LLM categorization feature that assigns a primary category to each note and integrates with the existing pipeline.

## Overview
- A new pipeline processor, CategoryClassifier, uses a Large Language Model to choose a single category from a configurable list.
- The selected category is stored in metadata['category'] and influences:
  - Tagging: optionally adds the category as a tag.
  - Folder organization: preferred mapping derives from the category.
- If the LLM is uncertain, the policy can either assign 'other' or attach suggestions (default: suggest). Suggestions may be free-form and are not limited to the configured category list.

## Configuration (ImportConfig)
New fields (defaults shown):
- enable_llm_categorization: false
- llm_provider: openai
- llm_model: gpt-4o-mini (example)
- llm_api_keys: mapping from provider -> ENV var name (no secrets in files)
- llm_base_url: optional OpenAI-compatible base URL (e.g., Ollama)
- llm_timeout_sec: 30
- llm_max_retries: 2
- llm_concurrency: 4
- llm_cache_enabled: true
- llm_cache_path: .cache/llm_category.jsonl
- llm_min_confidence: 0.6
- llm_head_chars: 2500
- llm_tail_chars: 500
- undecided_policy: other | suggest
- suggestions_count: 3
- propagate_category_tag: true
- propagate_suggested_categories_when_other: true  (if final category is 'other', add suggestions as tags)
- propagate_llm_suggested_tags: true  (merge llm_tags into tags)
- llm_prompt_template_path: null (optional path to a prompt template with placeholders)
- llm_prompt_version: v1 (changing this invalidates cache keys)
- llm_allow_freeform_suggestions: true (allow suggestions beyond configured slugs)
- llm_suggest_tags: true (ask model to return tags)
- llm_tags_max_count: 5
- llm_tags_min_count: 0
- categories: list of { name, slug, description }, including 'other'

## CLI Options
- --enable-llm
- --llm-provider openai|anthropic|ollama|vertex|groq
- --llm-model MODEL
- --llm-timeout SECONDS
- --llm-concurrency INT
- --llm-base-url URL

## Pipeline Order
When enable_llm_categorization=true, the processors run in this order:
1. CategoryClassifier (new)
2. TagInjector
3. FolderOrganizer
4. ContentTransformer
5. NoteSplitter (if enabled)

## CategoryClassifier
- Trims note content to head/tail to control token usage.
- Builds a strict JSON-only prompt including allowed slugs and their descriptions.
- Uses provider-specific client (OpenAI first) to classify.
- Confidence threshold (llm_min_confidence) controls assignment vs undecided.
- Cache (JSONL) is used to avoid repeated calls when enabled. Cache keys include the prompt version and a hash of the prompt template so changes invalidate cache entries.
- You can clear the cache at startup using the `--clear-llm-cache` CLI flag.
- Diagnostics stored in metadata (prefixed with _category_*) are for internal use.

## FolderOrganizer integration
- If metadata['category'] is set, it takes precedence for folder mapping.
- Uses custom_folder_rules when present, otherwise the slug as a folder path.
- Falls back to the existing tag/content heuristics when category is absent.

## TagInjector integration
- If propagate_category_tag=true and a category is chosen, ensures the category slug is present in tags.
- Continues to apply regex-based auto-tagging per existing rules.
- LLM-generated tags are stored in metadata.llm_tags and are normalized to kebab-case.
- If propagate_llm_suggested_tags=true, llm_tags are also merged into metadata.tags.
- If propagate_suggested_categories_when_other=true and the final category is 'other', category suggestions are merged into metadata.tags.

## Providers
- Uses the LiteLLM Python SDK to call multiple providers via a unified interface.
- Supported providers include OpenAI, Anthropic, Ollama (OpenAI-compatible), Vertex AI, Groq, and more via LiteLLM.
- Model identifiers can be provided as either `<provider>/<model>` (e.g., `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`) or as a plain model name with `llm_provider` indicating the provider. If `llm_model` contains a `/`, it is used as-is; otherwise the provider prefix is derived from `llm_provider`.
- API keys are read from standard environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`). If you prefer custom env var names, configure `ImportConfig.llm_api_keys` and the importer will map them to the standard variables at runtime.

## Implementation (LiteLLM)
- The classifier builds OpenAI-format messages and calls `litellm.completion()`.
- Provider prefix mapping used internally: `openai`, `anthropic`, `ollama`, `vertex_ai`, `groq`.
- `llm_base_url` is passed to LiteLLM as `api_base` (useful for OpenAI-compatible endpoints like a local Ollama gateway).
- Exceptions are mapped to OpenAI-style errors by LiteLLM; existing error handling continues to work.

## Progress Output
- During classification, the importer prints a lightweight progress line per note:
  - `[LLM] cache: <filename>` for cache hits
  - `[LLM] request: <filename>` when making a provider call
- This helps track long-running classification phases without changing existing CLI flags or behavior.

## Privacy & Testing
- No secrets are written to disk; only cache of classification outputs when enabled.
- Tests should mock any network calls and inject a fake client.
- To avoid committing caches, .cache/ is in .gitignore.
- When undecided policy is 'other', you can still propagate LLM signals via tags by enabling:
  - propagate_suggested_categories_when_other
  - propagate_llm_suggested_tags

## Examples
Enable LLM with OpenAI and a local endpoint (e.g., Ollama-compatible gateway):

```bash
OPENAI_API_KEY=$YOUR_KEY \
python import.py --smart \
  --enable-llm \
  --llm-provider openai \
  --llm-model gpt-4o-mini \
  --llm-base-url http://localhost:11434/v1
```