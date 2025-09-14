#!/usr/bin/env python3
"""
Generate an aggregate report of LLM-suggested categories and tags from the
.cache/llm_category.jsonl file produced by the importer.

Sections:
1) Suggested categories (distribution)
2) Tags by suggested category
3) Suggested tags with their category distribution

Usage:
  python scripts/generate_category_report.py \
    --input .cache/llm_category.jsonl \
    --output category_report.md
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple, Dict, Any


def norm_cat(s: str) -> str:
    return s.strip().lower()


def norm_tag(s: str) -> str:
    return s.strip().lower()


def sort_items(counter: Dict[str, int]):
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))


def iter_jsonl(path: Path) -> Iterable[Tuple[int, Dict[str, Any]]]:
    with path.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except Exception:
                # skip malformed lines silently (or print to stderr if preferred)
                continue


def generate_report(input_path: Path, output_path: Path) -> None:
    cat_counts: Counter = Counter()
    tags_by_cat: Dict[str, Counter] = defaultdict(Counter)
    cat_by_tag: Dict[str, Counter] = defaultdict(Counter)

    total_processed = 0

    for idx, rec in iter_jsonl(input_path):
        res = rec.get('result') or {}
        cat_raw = res.get('category_slug')
        # Treat missing/None as 'other' for aggregation
        cat = norm_cat(cat_raw) if isinstance(cat_raw, str) and cat_raw.strip() else 'other'

        tags = res.get('tags') or []
        if not isinstance(tags, (list, tuple)):
            # still count the category occurrence
            cat_counts[cat] += 1
            total_processed += 1
            continue

        tags_norm = [norm_tag(t) for t in tags if isinstance(t, str) and t.strip()]

        # Count the record itself
        cat_counts[cat] += 1
        total_processed += 1

        # De-duplicate tags within a single record before counting
        for t in set(tags_norm):
            tags_by_cat[cat][t] += 1
            cat_by_tag[t][cat] += 1

    if total_processed == 0:
        raise SystemExit("No valid records parsed from input JSONL.")

    ts = datetime.now().isoformat(timespec='seconds')
    md = []

    md.append('# LLM Category Report')
    md.append('')
    md.append(f'Generated: {ts}')
    md.append(f'Input: {input_path}')
    md.append(f'Total classified items: {total_processed}')
    md.append('')

    # Section 1: categories distribution
    md.append('## 1) Suggested categories (distribution)')
    md.append('')
    md.append('| Category | Count | Percent |')
    md.append('|---|---:|---:|')
    for cat, cnt in sort_items(cat_counts):
        pct = (cnt / total_processed) * 100 if total_processed else 0.0
        md.append(f'| {cat} | {cnt} | {pct:.1f}% |')
    md.append('')

    # Section 2: tags by category
    md.append('## 2) Tags by suggested category')
    md.append('')
    for cat, ccount in sort_items(cat_counts):
        md.append(f'### Category: {cat} (n={ccount})')
        md.append('')
        if ccount == 0 or not tags_by_cat.get(cat):
            md.append('_No tags observed for this category._')
            md.append('')
            continue
        md.append('| Tag | Count | Percent within category |')
        md.append('|---|---:|---:|')
        for tag, tcnt in sort_items(tags_by_cat[cat]):
            pct = (tcnt / ccount) * 100 if ccount else 0.0
            md.append(f'| {tag} | {tcnt} | {pct:.1f}% |')
        md.append('')

    # Section 3: tag -> category distribution
    md.append('## 3) Suggested tags with their category distribution')
    md.append('')
    if not cat_by_tag:
        md.append('_No tags found across records._')
    else:
        tag_totals = {t: sum(cat_cnt.values()) for t, cat_cnt in cat_by_tag.items()}
        for tag, ttot in sorted(tag_totals.items(), key=lambda kv: (-kv[1], kv[0])):
            md.append(f'### Tag: {tag} (n={ttot})')
            md.append('')
            md.append('| Category | Count | Percent of tag |')
            md.append('|---|---:|---:|')
            for cat, cnt in sort_items(cat_by_tag[tag]):
                pct = (cnt / ttot) * 100 if ttot else 0.0
                md.append(f'| {cat} | {cnt} | {pct:.1f}% |')
            md.append('')

    output_path.write_text('\n'.join(md), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='Generate LLM category/tag aggregate report from JSONL cache.')
    ap.add_argument('-i', '--input', default='.cache/llm_category.jsonl', help='Path to llm_category.jsonl (default: .cache/llm_category.jsonl)')
    ap.add_argument('-o', '--output', default='category_report.md', help='Path to write Markdown report (default: category_report.md)')
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    generate_report(in_path, out_path)
    print(f"Wrote report to: {out_path}")


if __name__ == '__main__':
    main()
