"""
Category Classifier Processor
Uses an LLM to assign a primary category to a note based on configured categories.
"""

import json
import hashlib
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re

from .base_processor import ContentProcessor
from litellm import completion as llm_completion


@dataclass
class _ClassificationResult:
    category_slug: Optional[str]
    confidence: float
    reasons: str
    suggestions: List[str]
    tags: List[str]
    undecided: bool = False


class CategoryClassifier(ContentProcessor):
    """Processor that classifies notes into categories using an LLM"""

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.cache_path = getattr(config, 'llm_cache_path', '.cache/llm_category.jsonl')
        self.cache_enabled = getattr(config, 'llm_cache_enabled', True)
        self.provider = getattr(config, 'llm_provider', 'openai')
        self.model = getattr(config, 'llm_model', None)
        self.base_url = getattr(config, 'llm_base_url', None)
        self.api_keys = getattr(config, 'llm_api_keys', {})
        self.min_conf = getattr(config, 'llm_min_confidence', 0.6)
        self.head_chars = getattr(config, 'llm_head_chars', 2500)
        self.tail_chars = getattr(config, 'llm_tail_chars', 500)
        self.undecided_policy = getattr(config, 'undecided_policy', 'other')
        self.suggestions_count = getattr(config, 'suggestions_count', 3)
        # Prompt and tags
        self.prompt_template_path = getattr(config, 'llm_prompt_template_path', None)
        self.prompt_version = getattr(config, 'llm_prompt_version', 'v1')
        self.allow_freeform = getattr(config, 'llm_allow_freeform_suggestions', True)
        self.suggest_tags = getattr(config, 'llm_suggest_tags', True)
        self.tags_max = getattr(config, 'llm_tags_max_count', 5)
        self.tags_min = getattr(config, 'llm_tags_min_count', 0)

        # Ensure cache directory exists if caching is enabled
        if self.cache_enabled:
            cache_dir = os.path.dirname(self.cache_path)
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)

    @property
    def name(self) -> str:
        return "category_classifier"

    def process(self, content: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        if not self.should_process(metadata, context):
            return content, metadata

        # Trim content to head/tail to control tokens
        trimmed = self._trim_text(content)

        categories = self._get_categories()
        allowed_slugs = [c['slug'] for c in categories]

        # Try cache
        cache_key = self._cache_key(trimmed, allowed_slugs)
        result = self._load_from_cache(cache_key)

        # Progress output (non-disruptive)
        fname = ''
        if isinstance(context, dict):
            fname = (context.get('filename') or '')
        if result is not None:
            print(f"[LLM] cache: {fname}")
        else:
            print(f"[LLM] request: {fname}")

        if result is None:
            # Call provider
            result = self._classify_with_provider(trimmed, categories)
            # Store in cache
            self._store_in_cache(cache_key, result, trimmed, allowed_slugs)

        # Apply undecided policy / confidence threshold
        updated = metadata.copy()
        if result.category_slug and not result.undecided and result.confidence >= self.min_conf and result.category_slug in allowed_slugs:
            updated['category'] = result.category_slug
        else:
            if self.undecided_policy == 'other':
                updated['category'] = 'other'
            elif self.undecided_policy == 'suggest':
                # leave category unset, add suggestions (free-form allowed, do not filter to allowed_slugs)
                suggestions = (result.suggestions or [])[: self.suggestions_count]
                if suggestions:
                    updated['_category_suggestions'] = suggestions

        # LLM-generated tags (stored separately, not merged into tags)
        if self.suggest_tags:
            llm_tags = self._normalize_tags(getattr(result, 'tags', []) if hasattr(result, 'tags') else [])
            # Enforce caps
            maxc = max(0, int(self.tags_max))
            llm_tags = llm_tags[:maxc] if maxc >= 0 else llm_tags
            updated['llm_tags'] = llm_tags

        # Attach diagnostics (not saved in frontmatter by default)
        updated['_category_confidence'] = result.confidence
        updated['_category_reasoning'] = result.reasons
        updated['_category_provider'] = self.provider
        updated['_category_model'] = self.model or ''
        updated['_category_prompt_version'] = self.prompt_version

        return content, updated

    def _trim_text(self, text: str) -> str:
        if len(text) <= self.head_chars + self.tail_chars:
            return text
        head = text[: self.head_chars]
        tail = text[-self.tail_chars :] if self.tail_chars > 0 else ''
        return head + "\n\n...\n\n" + tail

    def _get_categories(self) -> List[Dict[str, str]]:
        cats = getattr(self.config, 'categories', []) or []
        # ensure 'other' exists
        slugs = [c.get('slug') for c in cats]
        if 'other' not in slugs:
            cats.append({"name": "Other", "slug": "other", "description": "Fallback category."})
        return cats

    def _cache_key(self, trimmed_text: str, allowed_slugs: List[str]) -> str:
        template_text = self._load_prompt_template_text()
        template_hash = hashlib.sha256(template_text.encode('utf-8')).hexdigest()
        key_input = json.dumps({
            'text': trimmed_text,
            'slugs': sorted(allowed_slugs),
            'provider': self.provider,
            'model': self.model or '',
            'prompt_version': self.prompt_version,
            'template_hash': template_hash,
        }, sort_keys=True)
        return hashlib.sha256(key_input.encode('utf-8')).hexdigest()

    def _load_from_cache(self, key: str) -> Optional[_ClassificationResult]:
        if not self.cache_enabled or not os.path.exists(self.cache_path):
            return None
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        if rec.get('key') == key:
                            return _ClassificationResult(
                                category_slug=rec.get('result', {}).get('category_slug'),
                                confidence=rec.get('result', {}).get('confidence', 0.0),
                                reasons=rec.get('result', {}).get('reasons', ''),
                                suggestions=rec.get('result', {}).get('suggestions', []),
                                tags=rec.get('result', {}).get('tags', []),
                                undecided=rec.get('result', {}).get('undecided', False),
                            )
                    except Exception:
                        continue
        except Exception:
            return None
        return None

    def _store_in_cache(self, key: str, result: _ClassificationResult, trimmed_text: str, allowed_slugs: List[str]) -> None:
        if not self.cache_enabled:
            return
        try:
            with open(self.cache_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'key': key,
                    'result': {
                        'category_slug': result.category_slug,
                        'confidence': result.confidence,
                        'reasons': result.reasons,
                        'suggestions': result.suggestions,
                        'undecided': result.undecided,
                        'tags': getattr(result, 'tags', []),
                    }
                }) + "\n")
        except Exception:
            pass

    def _classify_with_provider(self, text: str, categories: List[Dict[str, str]]) -> _ClassificationResult:
        # Build prompt payload via template
        allowed_slugs = [c['slug'] for c in categories]
        allowed_display = ", ".join(allowed_slugs + (["other"] if 'other' not in allowed_slugs else []))
        descriptions = {c['slug']: c.get('description', '') for c in categories}
        template_text = self._load_prompt_template_text()
        rendered = template_text
        # Render placeholders (simple replacement)
        rendered = rendered.replace("{{llm_prompt_version}}", str(self.prompt_version))
        rendered = rendered.replace("{{allowed_slugs}}", allowed_display)
        rendered = rendered.replace("{{descriptions}}", json.dumps(descriptions, ensure_ascii=False))
        rendered = rendered.replace("{{suggestions_count}}", str(self.suggestions_count))
        rendered = rendered.replace("{{allow_freeform_suggestions}}", str(bool(self.allow_freeform)).lower())
        rendered = rendered.replace("{{suggest_tags}}", str(bool(self.suggest_tags)).lower())
        rendered = rendered.replace("{{tags_max_count}}", str(int(self.tags_max)))
        rendered = rendered.replace("{{min_confidence}}", str(float(self.min_conf)))
        rendered = rendered.replace("{{text}}", text)

        system_msg = { 'role': 'system', 'content': 'Respond ONLY with a JSON object, no prose.' }
        user_msg = { 'role': 'user', 'content': rendered }

        # Ensure env vars expected by LiteLLM, based on configured mapping
        self._ensure_provider_env()

        # Construct LiteLLM model identifier
        provider_prefix_map = {
            'openai': 'openai',
            'anthropic': 'anthropic',
            'ollama': 'ollama',
            'vertex': 'vertex_ai',  # LiteLLM uses 'vertex_ai'
            'groq': 'groq',
        }
        prefix = provider_prefix_map.get(self.provider, self.provider)
        model_name = self.model or 'gpt-4o-mini'
        litellm_model = model_name if '/' in model_name else f"{prefix}/{model_name}"

        kwargs = {
            'model': litellm_model,
            'messages': [system_msg, user_msg],
        }
        # Pass base URL if using an OpenAI-compatible endpoint (e.g., Ollama gateway)
        if self.base_url:
            kwargs['api_base'] = self.base_url

        try:
            resp = llm_completion(**kwargs)
            # LiteLLM returns OpenAI-format responses
            content = resp['choices'][0]['message']['content']
            # Strip code fences if any
            if isinstance(content, str) and content.strip().startswith("```"):
                # handle ```json ... ``` or ``` ... ```
                # handle ```json ... ``` or ``` ... ```
                parts = content.strip().split("\n", 1)
                if len(parts) == 2:
                    content = parts[1]
                content = content.strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
            result_obj = json.loads(content)

            cat = result_obj.get('category_slug')
            conf = float(result_obj.get('confidence', 0.0))
            reasons = result_obj.get('reasons', '')
            suggestions = result_obj.get('suggestions', []) or []
            tags = result_obj.get('tags', []) or []
            if cat not in allowed_slugs and cat != 'other':
                cat = None
            undecided = cat is None or conf < self.min_conf
            res = _ClassificationResult(
                category_slug=cat,
                confidence=conf,
                reasons=reasons,
                suggestions=suggestions,
                tags=tags,
                undecided=undecided,
            )
            return res
        except Exception as e:
            return _ClassificationResult(category_slug=None, confidence=0.0, reasons=str(e), suggestions=[], undecided=True)

    def _ensure_provider_env(self) -> None:
        """Ensure standard env vars for providers are populated from configured mapping if needed."""
        try:
            # Map provider -> standard env var name used by LiteLLM
            std_env = {
                'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'groq': 'GROQ_API_KEY',
            }
            std_name = std_env.get(self.provider)
            if not std_name:
                return
            custom_env_var = (self.api_keys or {}).get(self.provider)
            if custom_env_var and not os.environ.get(std_name):
                val = os.environ.get(custom_env_var)
                if val:
                    os.environ[std_name] = val
        except Exception:
            # Ignore env setup failures silently
            pass

    def _load_prompt_template_text(self) -> str:
        """Load prompt template from file if configured, otherwise return default template."""
        default_template = (
            "LLM Prompt Version: {{llm_prompt_version}}\n\n"
            "You are a JSON-only classifier. Read the note text and respond with a single JSON object. Do not include any extra text.\n\n"
            "Allowed primary category slugs (choose exactly one or 'other' for primary):\n"
            "{{allowed_slugs}}\n\n"
            "Category descriptions:\n"
            "{{descriptions}}\n\n"
            "Instructions:\n"
            "- Choose primary category_slug only from the allowed list or 'other'. Never invent a new slug for the primary category.\n"
            "- Provide confidence between 0 and 1 (float). Aim to reflect your certainty.\n"
            "- Provide a brief reasons string.\n"
            "- Provide suggestions: a single array of alternative categories. These MAY be free-form and are NOT limited to the allowed list. Limit to at most {{suggestions_count}} suggestions. Free-form suggestions allowed: {{allow_freeform_suggestions}}.\n"
            "- Tags: If {{suggest_tags}} is true, include an array of topical tags (not prefixed with '#') that describe the note. Limit to at most {{tags_max_count}} items. Tags may be free-form.\n"
            "- Return only valid JSON; no markdown.\n\n"
            "Respond as JSON with this schema:\n"
            "{\n"
            "  \"category_slug\": \"one-of-allowed-or-other-or-null\",\n"
            "  \"confidence\": 0.0,\n"
            "  \"reasons\": \"short explanation\",\n"
            "  \"suggestions\": [\"free form\", \"or from allowed\", \"...\"],\n"
            "  \"tags\": [\"topic-1\", \"topic 2\", \"etc\"]\n"
            "}\n\n"
            "Minimum confidence threshold for assignment: {{min_confidence}}\n\n"
            "Note text (truncated):\n"
            "{{text}}\n"
        )
        try:
            if self.prompt_template_path and os.path.exists(self.prompt_template_path):
                with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return default_template

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        norm = []
        seen = set()
        for t in tags or []:
            s = str(t).strip().lower()
            s = s.replace('_', '-').replace(' ', '-')
            s = re.sub(r"[^a-z0-9\-]+", '-', s)
            s = re.sub(r"-{2,}", '-', s)
            s = s.strip('-')
            if s and s not in seen:
                seen.add(s)
                norm.append(s)
        return norm
