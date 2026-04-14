#!/usr/bin/env python3
"""Search Typst API using a pre-computed BM25 index.

Usage:
    python3 scripts/search-api.py "position slice string"
    python3 scripts/search-api.py "image width" --top 5
    python3 scripts/search-api.py "query heading" --kind method
    python3 scripts/search-api.py "color" --kind type --json
    python3 scripts/search-api.py --name str.position
    python3 scripts/search-api.py --list-categories
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict


def tokenize(text):
    """Lowercase, split on non-alphanumeric, keep all tokens including 1-char."""
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_data_dir(override):
    if override:
        return override
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "..", "data")


def bm25_search(query_tokens, bm25, top_n=20):
    """Score documents against query using BM25."""
    scores = defaultdict(float)
    meta = bm25["meta"]
    avg_dl = meta["avg_dl"]
    k1 = meta["k1"]
    b = meta["b"]

    for token in query_tokens:
        idf_val = bm25["idf"].get(token, 0)
        if idf_val == 0:
            continue
        for doc_id_str, tf in bm25["postings"].get(token, []):
            doc_id = int(doc_id_str) if isinstance(doc_id_str, str) else doc_id_str
            dl = bm25["doc_lengths"].get(
                str(doc_id), bm25["doc_lengths"].get(doc_id, avg_dl)
            )
            # Cap doc length to prevent over-penalizing long documents
            dl = min(dl, avg_dl * 3)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * dl / avg_dl)
            scores[doc_id] += idf_val * numerator / denominator

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return ranked[:top_n]


def format_params(params):
    """Format parameter list for display."""
    parts = []
    for p in params:
        types = "|".join(p.get("types", []))
        name = p["name"]
        if p.get("required"):
            parts.append(f"{name}: {types}")
        else:
            default = p.get("default", "")
            if default:
                parts.append(f"{name}: {types} = {default}")
            else:
                parts.append(f"{name}: {types}?")
    return ", ".join(parts)


def format_entry(entry, verbose=False):
    """Format a single API entry for display."""
    if entry.get("kind") == "symbol":
        value = entry.get("value", "")
        lines = [f"{entry['name']}  {value}"]
        parts = []
        if entry.get("mathShorthand"):
            parts.append(f"math: {entry['mathShorthand']}")
        if entry.get("markupShorthand"):
            parts.append(f"markup: {entry['markupShorthand']}")
        if parts:
            lines.append(f"  shorthand: {', '.join(parts)}")
        return "\n".join(lines)

    params = format_params(entry.get("params", []))
    returns = "|".join(entry.get("returns", []))
    sig = f"{entry['name']}({params})"
    if returns:
        sig += f" -> {returns}"

    lines = [sig]
    lines.append(f"  {entry.get('oneliner', '')}")
    if verbose:
        lines.append(
            f"  [{entry['kind']}] category: {entry['category']} | docs: https://typst.app/docs{entry.get('route', '')}"
        )
        if entry.get("contextual"):
            lines.append("  requires context")
        if entry.get("deprecated"):
            lines.append(f"  DEPRECATED: {entry['deprecated']}")
        # Show enum values for string params
        for p in entry.get("params", []):
            if p.get("strings"):
                lines.append(
                    f"  {p['name']} values: {', '.join(repr(s) for s in p['strings'])}"
                )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Typst API reference.")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--top", type=int, default=10, help="Number of results")
    parser.add_argument(
        "--kind",
        choices=["function", "method", "constructor", "type", "symbol"],
        help="Filter by kind",
    )
    parser.add_argument(
        "--category", help="Filter by category (e.g., Foundations, Layout)"
    )
    parser.add_argument("--name", help="Exact name lookup (e.g., str.position)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show more details"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="List all categories"
    )
    parser.add_argument("--data-dir", help="Override data directory")
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.data_dir)
    api = load_json(os.path.join(data_dir, "api.json"))

    if args.list_categories:
        cats = sorted(set(e["category"] for e in api))
        for c in cats:
            count = sum(1 for e in api if e["category"] == c)
            print(f"  {c} ({count})")
        return

    if args.name:
        matches = [e for e in api if e["name"] == args.name]
        if not matches:
            # Try partial match
            matches = [e for e in api if args.name in e["name"]]
        if not matches:
            print(f"No entry found for '{args.name}'", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(matches, indent=2))
        else:
            for e in matches:
                print(format_entry(e, verbose=True))
                print()
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    bm25 = load_json(os.path.join(data_dir, "api-bm25.json"))
    tokens = tokenize(args.query)
    if not tokens:
        print("No searchable terms in query", file=sys.stderr)
        sys.exit(1)

    # Pre-filter by kind/category before BM25 to avoid missing matches
    candidate_ids = set(range(len(api)))
    if args.kind:
        candidate_ids = {i for i in candidate_ids if api[i]["kind"] == args.kind}
    if args.category:
        candidate_ids = {
            i
            for i in candidate_ids
            if args.category.lower() in api[i]["category"].lower()
        }

    results = bm25_search(tokens, bm25, top_n=len(api))

    # Use explicit --top if set, otherwise default higher for symbols
    top_n = args.top

    filtered = []
    for doc_id, score in results:
        if doc_id not in candidate_ids:
            continue
        # Apply category weight multiplier
        weight = api[doc_id].get("weight", 1.0)
        filtered.append((api[doc_id], score * weight))
        if len(filtered) >= top_n * 3:
            break

    # Re-sort after weight adjustment
    filtered.sort(key=lambda x: -x[1])
    filtered = filtered[:top_n]

    if not filtered:
        print("No results found", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps([e for e, _ in filtered], indent=2))
    else:
        for i, (entry, score) in enumerate(filtered, 1):
            print(f"{i:2}. {format_entry(entry, verbose=args.verbose)}")
            print()


if __name__ == "__main__":
    main()
