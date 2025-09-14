# LLM-based Note Categorization

This document describes the LLM categorization feature that assigns a primary category to each note and integrates with the existing pipeline.

## Overview
- A new pipeline processor, CategoryClassifier, uses a Large Language Model to choose a single category from a configurable list.
- The selected category is stored in metadata['category'] and influences:
  - Tagging: optionally adds the category as a tag.
  - Folder organization: preferred mapping derives from the category.
- If the LLM is uncertain, the policy can either assign 'other' or attach suggestions.

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
- Cache (JSONL) is used to avoid repeated calls when enabled.
- Diagnostics stored in metadata (prefixed with _category_*) are for internal use.

## FolderOrganizer integration
- If metadata['category'] is set, it takes precedence for folder mapping.
- Uses custom_folder_rules when present, otherwise the slug as a folder path.
- Falls back to the existing tag/content heuristics when category is absent.

## TagInjector integration
- If propagate_category_tag=true and a category is chosen, ensures the category slug is present in tags.
- Continues to apply regex-based tag rules in addition to category propagation.

## Providers
- OpenAI is supported initially via the chat/completions API and JSON mode.
- Other providers (Anthropic, Ollama, etc.) can be added behind the same abstraction.
- API keys are read from environment variables (names configured via ImportConfig.llm_api_keys).

## Privacy & Testing
- No secrets are written to disk; only cache of classification outputs when enabled.
- Tests should mock any network calls and inject a fake client.
- To avoid committing caches, .cache/ is in .gitignore.

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