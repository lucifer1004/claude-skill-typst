#!/usr/bin/env python3
"""Build Typst API index from Typst API JSON data.

Requires building `typst-docs` from the Typst compiler repo first:
    git clone --depth 1 https://github.com/typst/typst /tmp/typst-repo
    cd /tmp/typst-repo && cargo build -p typst-docs --release
    ./target/release/typst-docs --out-file /tmp/typst-api-raw.json

Then run this script:
    python3 tools/fetch-api-docs.py /tmp/typst-api-raw.json

This is a dev/CI tool, NOT part of the distributed skill bundle.
"""

import argparse
import json
import math
import os
import re
import urllib.request
from collections import defaultdict

UNICODE_MATH_URL = (
    "https://raw.githubusercontent.com/wspr/unicode-math/master/unicode-math-table.tex"
)


def fetch_latex_aliases():
    """Fetch unicode-math-table.tex and build {unicode_char: [latex_names]} mapping."""
    try:
        with urllib.request.urlopen(UNICODE_MATH_URL, timeout=30) as resp:
            text = resp.read().decode("utf-8")
    except Exception as e:
        print(f"Warning: could not fetch unicode-math-table: {e}")
        return {}

    # Parse: \UnicodeMathSymbol{"XXXXX}{\commandname ...}{\mathclass}{description}
    pattern = re.compile(r'\\UnicodeMathSymbol\{"([0-9A-F]+)\}\{\\(\w+)\s*\}')
    mapping = defaultdict(list)
    for m in pattern.finditer(text):
        codepoint = int(m.group(1), 16)
        latex_name = m.group(2)
        try:
            char = chr(codepoint)
            mapping[char].append(latex_name)
        except (ValueError, OverflowError):
            pass

    print(
        f"Loaded {sum(len(v) for v in mapping.values())} LaTeX aliases for {len(mapping)} Unicode chars"
    )
    return mapping


_MATH_SUBWORDS = {
    "arrow",
    "right",
    "left",
    "up",
    "down",
    "long",
    "double",
    "triple",
    "equal",
    "less",
    "greater",
    "plus",
    "minus",
    "times",
    "not",
    "big",
    "small",
    "circle",
    "square",
    "triangle",
    "diamond",
    "open",
    "close",
    "angle",
    "curly",
    "round",
    "hat",
    "bar",
    "dot",
    "tilde",
    "check",
    "vec",
    "over",
    "under",
    "brace",
    "bracket",
    "paren",
    "head",
    "tail",
    "hook",
    "two",
    "integral",
    "sum",
    "prod",
}


def _split_compound(word):
    """Split compound LaTeX name into known subwords.
    'rightarrow' → ['right', 'arrow'], 'leftrightarrow' → ['left', 'right', 'arrow']
    Returns subword list, or empty list if no valid split found."""
    if len(word) <= 5:
        return []
    # Try all split positions, greedy longest-first
    parts = []
    remaining = word
    while remaining:
        found = False
        for length in range(min(len(remaining), 10), 2, -1):
            prefix = remaining[:length]
            if prefix in _MATH_SUBWORDS:
                parts.append(prefix)
                remaining = remaining[length:]
                found = True
                break
        if not found:
            break
    # Only return if we consumed most of the word
    consumed = sum(len(p) for p in parts)
    if consumed >= len(word) * 0.7 and len(parts) >= 2:
        return parts
    return []


BM25_K1 = 1.5
BM25_B = 0.75
NAME_BOOST = 3
ONELINER_BOOST = 2
PARAM_BOOST = 1

# Category relevance weights applied as score multipliers during search.
# Core Typst categories are boosted; experimental export categories are dampened.
CATEGORY_WEIGHT = {
    "Foundations": 1.5,
    "Model": 1.5,
    "Text": 1.5,
    "Math": 1.5,
    "Layout": 1.5,
    "Visualize": 1.5,
    "Introspection": 1.5,
    "Data Loading": 1.5,
    "Symbols": 1.0,
    "HTML": 0.3,
    "PDF": 0.5,
}

# Expand single-letter abbreviations in symbol names for better search
# Typst abbreviation → full English words for search expansion.
# Applied at index time so "paragraph indent" matches `par`.
NAME_EXPANSIONS = {
    "par": ["paragraph"],
    "eq": ["equal", "equals"],
    "neq": ["notequal"],
    "lt": ["less"],
    "gt": ["greater"],
    "str": ["string"],
    "int": ["integer"],
    "bool": ["boolean"],
    "dict": ["dictionary"],
    "emph": ["emphasis", "italic"],
    "auto": ["automatic"],
    "eval": ["evaluate"],
    "calc": ["calculation", "math"],
    "repr": ["representation", "debug"],
    "sym": ["symbol"],
    "text": ["font", "typography"],
}

# Ordered longest-first to avoid partial matches (.t before .tr)
# Each entry: (abbrev, expansion for tokenization)
# Compound expansions use dots so they tokenize as separate words
SYMBOL_ABBREV = [
    (".ccw", ".counter.clockwise"),
    (".tr", ".top.right"),
    (".bl", ".bottom.left"),
    (".tl", ".top.left"),
    (".br", ".bottom.right"),
    (".cw", ".clockwise"),
    (".r", ".right"),
    (".l", ".left"),
    (".t", ".top"),
    (".b", ".bottom"),
]


def tokenize(text):
    """Lowercase, split on non-alphanumeric, keep all tokens including 1-char."""
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def extract_functions(raw_json):
    """Extract all functions, types, and methods from typst-docs JSON."""
    entries = []
    ref = raw_json[2]  # Reference section

    for category in ref.get("children", []):
        cat_name = category.get("title", "")

        for page in category.get("children", []):
            body = page.get("body", {})
            kind = body.get("kind", "")
            content = body.get("content", {})
            route = page.get("route", "")

            if kind == "func":
                entry = _extract_func(content, cat_name, route)
                entries.append(entry)
                # Scope methods
                for method in content.get("scope", []):
                    m_entry = _extract_func(
                        method, cat_name, route, parent=content.get("name", "")
                    )
                    entries.append(m_entry)

            elif kind == "type":
                # Type entry itself
                type_entry = {
                    "name": content.get("name", ""),
                    "category": cat_name,
                    "kind": "type",
                    "oneliner": content.get("oneliner", ""),
                    "params": [],
                    "returns": [],
                    "route": route,
                    "weight": CATEGORY_WEIGHT.get(cat_name, 1.0),
                }
                entries.append(type_entry)
                # Constructor
                constructor = content.get("constructor")
                if constructor:
                    entry = _extract_func(
                        constructor, cat_name, route, is_constructor=True
                    )
                    entries.append(entry)
                # Scope methods
                for method in content.get("scope", []):
                    m_entry = _extract_func(
                        method, cat_name, route, parent=content.get("name", "")
                    )
                    entries.append(m_entry)

            elif kind == "symbols":
                for sym in content.get("list", []):
                    entry = _extract_symbol(sym, cat_name, route)
                    entries.append(entry)

            elif kind == "group":
                for func in content.get("functions", []):
                    entry = _extract_func(func, cat_name, route)
                    entries.append(entry)
                    for method in func.get("scope", []):
                        m_entry = _extract_func(
                            method, cat_name, route, parent=func.get("name", "")
                        )
                        entries.append(m_entry)

    return entries


def _strip_html(text):
    """Remove HTML tags and decode entities."""
    if not text or not isinstance(text, str):
        return text
    import html

    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def _extract_func(data, category, route, parent=None, is_constructor=False):
    """Extract a single function/method entry."""
    name = data.get("name", "")
    if parent:
        full_name = f"{parent}.{name}"
    else:
        full_name = name

    params = []
    for p in data.get("params", []):
        param = {
            "name": p.get("name", ""),
            "types": p.get("types", []),
            "required": p.get("required", False),
        }
        default = p.get("default")
        if default is not None:
            param["default"] = (
                _strip_html(default) if isinstance(default, str) else default
            )
        strings = p.get("strings")
        if strings:
            param["strings"] = [
                s.get("string", s) if isinstance(s, dict) else s for s in strings
            ]
        params.append(param)

    kind_val = "constructor" if is_constructor else ("method" if parent else "function")
    entry = {
        "name": full_name,
        "category": category,
        "kind": kind_val,
        "oneliner": data.get("oneliner", ""),
        "params": params,
        "returns": data.get("returns", []),
        "route": route,
        "weight": CATEGORY_WEIGHT.get(category, 1.0),
    }

    if data.get("contextual"):
        entry["contextual"] = True
    if data.get("element"):
        entry["element"] = True
    if data.get("deprecationMessage"):
        entry["deprecated"] = data["deprecationMessage"]

    return entry


def _extract_symbol(data, category, route):
    """Extract a single symbol entry."""
    name = data.get("name", "")
    value = data.get("value", "")
    math_shorthand = data.get("mathShorthand") or ""
    markup_shorthand = data.get("markupShorthand") or ""

    # Build oneliner: "→  (sym.arrow.r, math: ->)"
    parts = [f"sym.{name}"]
    if math_shorthand:
        parts.append(f"math: {math_shorthand}")
    if markup_shorthand:
        parts.append(f"markup: {markup_shorthand}")
    oneliner = f"{value}  ({', '.join(parts)})"

    entry = {
        "name": f"sym.{name}",
        "category": category,
        "kind": "symbol",
        "oneliner": oneliner,
        "value": value,
        "params": [],
        "returns": [],
        "route": route,
        "weight": CATEGORY_WEIGHT.get(category, 1.0),
    }
    if math_shorthand:
        entry["mathShorthand"] = math_shorthand
    if markup_shorthand:
        entry["markupShorthand"] = markup_shorthand
    if data.get("accent"):
        entry["accent"] = True

    return entry


def build_bm25_index(entries, latex_aliases=None):
    """Build BM25 inverted index over API entries."""
    latex_aliases = latex_aliases or {}
    postings = defaultdict(list)
    doc_lengths = {}
    idf = {}
    term_doc_count = defaultdict(int)

    for i, entry in enumerate(entries):
        tokens = []
        name = entry["name"]
        # Expand symbol abbreviations for searchability
        if entry.get("kind") == "symbol":
            expanded = name
            for abbr, full in SYMBOL_ABBREV:
                # Only replace when abbr is a complete path segment (followed by . or end)
                expanded = re.sub(re.escape(abbr) + r"(?=\.|$)", full, expanded)
            expanded_tokens = tokenize(expanded)
            tokens.extend(expanded_tokens * NAME_BOOST)
            for et in expanded_tokens:
                for expansion in NAME_EXPANSIONS.get(et, []):
                    tokens.extend(tokenize(expansion) * NAME_BOOST)
        else:
            name_tokens = tokenize(name)
            tokens.extend(name_tokens * NAME_BOOST)
            # Expand abbreviated names for searchability
            for nt in name_tokens:
                for expansion in NAME_EXPANSIONS.get(nt, []):
                    tokens.extend(tokenize(expansion) * NAME_BOOST)
        tokens.extend(tokenize(entry.get("oneliner", "")) * ONELINER_BOOST)
        tokens.extend(tokenize(entry.get("category", "")))
        for p in entry.get("params", []):
            tokens.extend(tokenize(p["name"]) * PARAM_BOOST)
            for t in p.get("types", []):
                tokens.extend(tokenize(t))
            for s in p.get("strings", [])[:10]:  # cap to avoid doc_length bloat
                tokens.extend(tokenize(s) * PARAM_BOOST)
        # Symbol-specific: index shorthands and LaTeX aliases
        if entry.get("mathShorthand"):
            tokens.extend(tokenize(entry["mathShorthand"]) * NAME_BOOST)
        if entry.get("markupShorthand"):
            tokens.extend(tokenize(entry["markupShorthand"]) * NAME_BOOST)
        if entry.get("kind") == "symbol" and entry.get("value"):
            for latex_name in latex_aliases.get(entry["value"], []):
                latex_tokens = tokenize(latex_name)
                tokens.extend(latex_tokens * NAME_BOOST)
                # Split compound names (e.g., "rightarrow" → "right"+"arrow")
                for lt in latex_tokens:
                    for part in _split_compound(lt):
                        tokens.extend([part] * NAME_BOOST)

        doc_lengths[i] = len(tokens)

        tf = defaultdict(int)
        for t in tokens:
            tf[t] += 1
        seen = set()
        for t, count in tf.items():
            postings[t].append((i, count))
            if t not in seen:
                term_doc_count[t] += 1
                seen.add(t)

    num_docs = len(entries)
    avg_dl = sum(doc_lengths.values()) / max(num_docs, 1)

    for term, doc_count in term_doc_count.items():
        idf[term] = math.log((num_docs - doc_count + 0.5) / (doc_count + 0.5) + 1)

    return {
        "meta": {
            "num_docs": num_docs,
            "avg_dl": round(avg_dl, 2),
            "k1": BM25_K1,
            "b": BM25_B,
        },
        "idf": {k: round(v, 4) for k, v in idf.items()},
        "postings": {k: v for k, v in postings.items()},
        "doc_lengths": doc_lengths,
        "doc_names": {i: e["name"] for i, e in enumerate(entries)},
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build Typst API index from Typst API JSON data."
    )
    parser.add_argument("input", help="Path to input JSON")
    parser.add_argument(
        "--input-format",
        choices=["typst-docs-json", "entries"],
        default="typst-docs-json",
        help=(
            "Input JSON format: old typst-docs page tree or normalized "
            "api.json-style entries"
        ),
    )
    parser.add_argument(
        "--output-stem",
        default="api",
        help="Output filename stem, e.g. 'api' or 'api-main'",
    )
    parser.add_argument(
        "--out-dir",
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "skills",
            "typst",
            "data",
        ),
        help="Output directory for api.json and api-bm25.json",
    )
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.output_stem):
        parser.error("--output-stem must be a filename stem, not a path")

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if args.input_format == "entries":
        if not isinstance(raw, list):
            parser.error("--input-format entries expects a JSON array")
        entries = raw
    else:
        entries = extract_functions(raw)
    print(f"Extracted {len(entries)} API entries")

    # Count by kind
    kinds = defaultdict(int)
    for e in entries:
        kinds[e["kind"]] += 1
    for k, v in sorted(kinds.items()):
        print(f"  {k}: {v}")

    os.makedirs(args.out_dir, exist_ok=True)

    api_path = os.path.join(args.out_dir, f"{args.output_stem}.json")
    with open(api_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {api_path} ({os.path.getsize(api_path)} bytes)")

    latex_aliases = fetch_latex_aliases()
    bm25 = build_bm25_index(entries, latex_aliases=latex_aliases)
    bm25_path = os.path.join(args.out_dir, f"{args.output_stem}-bm25.json")
    with open(bm25_path, "w", encoding="utf-8") as f:
        json.dump(bm25, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {bm25_path} ({os.path.getsize(bm25_path)} bytes)")


if __name__ == "__main__":
    main()
