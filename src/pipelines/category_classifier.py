"""
Category Classifier Processor
Uses an LLM to assign a primary category to a note based on configured categories.
"""

import json
import hashlib
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .base_processor import ContentProcessor


@dataclass
class _ClassificationResult:
    category_slug: Optional[str]
    confidence: float
    reasons: str
    suggestions: List[str]
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
                # leave category unset, add suggestions
                suggestions = [s for s in result.suggestions if s in allowed_slugs][: self.suggestions_count]
                if suggestions:
                    updated['_category_suggestions'] = suggestions

        # Attach diagnostics (not saved in frontmatter by default)
        updated['_category_confidence'] = result.confidence
        updated['_category_reasoning'] = result.reasons
        updated['_category_provider'] = self.provider
        updated['_category_model'] = self.model or ''

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
        key_input = json.dumps({
            'text': trimmed_text,
            'slugs': sorted(allowed_slugs),
            'provider': self.provider,
            'model': self.model or ''
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
                    }
                }) + "\n")
        except Exception:
            pass

    def _classify_with_provider(self, text: str, categories: List[Dict[str, str]]) -> _ClassificationResult:
        # Build prompt payload
        allowed_slugs = [c['slug'] for c in categories]
        descriptions = {c['slug']: c.get('description', '') for c in categories}

        user_prompt = (
            "You are a strict JSON generator. Given the note text, classify it into exactly one of the allowed category slugs or 'other'.\n"
            "Return ONLY a JSON object with fields: category_slug, confidence (0..1), reasons (short), suggestions (array of slugs).\n\n"
            f"Allowed slugs: {allowed_slugs}\n"
            f"Descriptions: {descriptions}\n\n"
            f"Text:\n{text}\n"
        )

        # Provider selection (OpenAI first; others can be added later)
        if self.provider == 'openai':
            return self._classify_openai(user_prompt, allowed_slugs)
        # Fallback: return undecided to be safe
        return _ClassificationResult(category_slug=None, confidence=0.0, reasons='Provider not implemented', suggestions=[], undecided=True)

    def _classify_openai(self, user_prompt: str, allowed_slugs: List[str]) -> _ClassificationResult:
        # Resolve API key env var name from config
        api_env_name = self.api_keys.get('openai') or 'OPENAI_API_KEY'
        api_key = os.environ.get(api_env_name)
        if not api_key:
            return _ClassificationResult(category_slug=None, confidence=0.0, reasons=f'Missing {api_env_name}', suggestions=allowed_slugs[:2], undecided=True)

        import json as _json
        import urllib.request as _req
        import urllib.error as _err

        url = (self.base_url or 'https://api.openai.com/v1') + '/chat/completions'
        model = self.model or 'gpt-4o-mini'
        payload = {
            'model': model,
            'messages': [
                { 'role': 'system', 'content': 'Respond ONLY with a JSON object, no prose.' },
                { 'role': 'user', 'content': user_prompt }
            ],
            'temperature': 0.0,
            'response_format': { 'type': 'json_object' }
        }
        data = _json.dumps(payload).encode('utf-8')
        req = _req.Request(url, data=data, headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        try:
            with _req.urlopen(req, timeout=getattr(self.config, 'llm_timeout_sec', 30)) as resp:
                body = resp.read().decode('utf-8')
        except _err.HTTPError as e:
            return _ClassificationResult(category_slug=None, confidence=0.0, reasons=f'HTTP {e.code}', suggestions=[], undecided=True)
        except Exception as e:
            return _ClassificationResult(category_slug=None, confidence=0.0, reasons=str(e), suggestions=[], undecided=True)

        try:
            parsed = _json.loads(body)
            content = parsed['choices'][0]['message']['content']
            result_obj = _json.loads(content)
            cat = result_obj.get('category_slug')
            if cat not in allowed_slugs and cat != 'other':
                cat = None
            conf = float(result_obj.get('confidence', 0.0))
            reasons = result_obj.get('reasons', '')
            suggestions = result_obj.get('suggestions', [])
            undecided = cat is None or conf < self.min_conf
            return _ClassificationResult(category_slug=cat, confidence=conf, reasons=reasons, suggestions=suggestions, undecided=undecided)
        except Exception:
            return _ClassificationResult(category_slug=None, confidence=0.0, reasons='Parse error', suggestions=[], undecided=True)
