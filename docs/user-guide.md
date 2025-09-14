# User Guide

This guide walks you through using the SimpleNote → Obsidian importer, including the new LLM-based categorization feature.

## Overview
- Converts SimpleNote exports (.txt files plus source/notes.json) into Obsidian-friendly Markdown with YAML frontmatter.
- Phase 2 features include Auto-tagging, Folder Organization, and Content Transformation.
- Optional Phase 3 features include Note Splitting and LLM-based Note Categorization.

Pipeline when LLM categorization is enabled:
1) CategoryClassifier (LLM) → sets metadata.category
2) TagInjector → adds tags based on rules and can propagate the category
3) FolderOrganizer → prefers category for folder mapping
4) ContentTransformer → formatting and cleanup
5) NoteSplitter (if enabled)

## Quick Start
```bash
# Basic import from current directory
python import.py

# Smart processing with default settings
python import.py --smart --notes data --json data/source/notes.json

# Use a preset
python import.py --preset organized --notes data --json data/source/notes.json
```

## Presets
- minimal: Phase 1 compatibility, no smart processing
- basic: Auto-tagging + content transformation
- organized: Full smart processing with folder organization
- full: All features including index files and backlinks
- phase3: Enables advanced features including note splitting

## Enabling LLM-Based Categorization

1) Export and set your provider API key(s) as environment variables (never in files):
- OpenAI: export OPENAI_API_KEY={{OPENAI_API_KEY}}
- Anthropic: export ANTHROPIC_API_KEY={{ANTHROPIC_API_KEY}}
- Groq: export GROQ_API_KEY={{GROQ_API_KEY}}
- Vertex: export GOOGLE_APPLICATION_CREDENTIALS={{GOOGLE_APPLICATION_CREDENTIALS}}
- Ollama: often not required; may run locally without API keys

2) Run with CLI flags:
```bash
python import.py --smart \
  --enable-llm \
  --llm-provider openai \
  --llm-model gpt-4o-mini

# OpenAI-compatible local gateway (e.g., Ollama)
python import.py --smart \
  --enable-llm \
  --llm-provider openai \
  --llm-model gpt-4o-mini \
  --llm-base-url http://localhost:11434/v1

# Tuning
python import.py --smart \
  --enable-llm \
  --llm-provider openai \
  --llm-model gpt-4o-mini \
  --llm-timeout 30 \
  --llm-concurrency 4
```

3) Or configure in YAML (recommended). Start from the full sample:
- Copy config/sample_config_full.yaml to config/my_settings.yaml and edit.
- Then run: python import.py --config config/my_settings.yaml --notes data --json data/source/notes.json

## How categorization affects tags and folders
- The selected category is placed in metadata.category.
- If propagate_category_tag is true, the category slug is ensured in tags.
- Folder mapping prefers metadata.category when present. Custom folder rules can map slugs to nested paths.

## Provider setup notes
- OpenAI: requires OPENAI_API_KEY and model (e.g., gpt-4o-mini). No base URL needed.
- Ollama: run a local OpenAI-compatible endpoint, e.g., http://localhost:11434/v1, usually no API key.
- Anthropic, Vertex, Groq: configure API keys and ensure llm_provider matches; set model names per provider.

## Troubleshooting
- Missing API key: ensure the environment variable name matches llm_api_keys in your YAML.
- Timeouts/retries: adjust llm_timeout_sec and llm_max_retries.
- Rate limits: lower llm_concurrency.
- Cache: results are written to .cache/llm_category.jsonl (git-ignored). Delete the file to reclassify.
- Base URL mismatch: ensure llm_base_url is set only for OpenAI-compatible endpoints (Ollama). Leave null for hosted APIs.

## FAQ
- How to reduce cost? Lower llm_head_chars and llm_tail_chars; increase llm_min_confidence; use suggest policy.
- Can I run locally? Yes, via an OpenAI-compatible local service (e.g., Ollama) and set llm_base_url.
- Do I need categories? Provide your own category set in YAML; include a fallback 'other' slug.

## References
- docs/llm-categorization.md
- config/sample_config_full.yaml