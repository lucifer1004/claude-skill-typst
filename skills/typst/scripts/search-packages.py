#!/usr/bin/env python3
"""Search Typst Universe packages using a pre-computed BM25 index.

Composite scoring: BM25 relevance * recency boost * maturity boost.
Compatibility filtering: excludes packages requiring a newer Typst compiler.

Usage:
    python3 search-packages.py "chart plotting visualization"
    python3 search-packages.py "timeline" --category visualization
    python3 search-packages.py --category cv --top 5
    python3 search-packages.py "chart" --json
    python3 search-packages.py --list-categories
    python3 search-packages.py --list-disciplines
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import defaultdict

RECENCY_WEIGHT = 0.2
RECENCY_HALF_LIFE_DAYS = 365
MATURITY_WEIGHT = 0.1


def tokenize(text):
    """Lowercase, split on non-alphanumeric, drop tokens <= 1 char."""
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 1]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_data_dir(override):
    if override:
        return override
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "..", "data")


def parse_version(v):
    """Parse version string to comparable tuple. Returns (0,0,0) on failure."""
    if not v:
        return (0, 0, 0)
    parts = []
    for seg in v.split(".")[:3]:
        try:
            parts.append(int(seg))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def detect_typst_version():
    """Run `typst --version` and parse the version number."""
    try:
        result = subprocess.run(
            ["typst", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
            if match:
                return match.group(1)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def bm25_search(query_tokens, index):
    """Score all documents against query tokens using BM25."""
    meta = index["meta"]
    k1 = meta["k1"]
    b = meta["b"]
    avg_dl = meta["avg_dl"]
    doc_lengths = index["doc_lengths"]
    idf = index["idf"]
    postings = index["postings"]

    scores = defaultdict(float)

    for token in query_tokens:
        if token not in postings:
            continue
        token_idf = idf.get(token, 0)
        for doc_idx, tf in postings[token]:
            dl = doc_lengths[doc_idx]
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * dl / avg_dl)
            scores[doc_idx] += token_idf * numerator / denominator

    return scores


def recency_score(updated_at):
    """Exponential decay: 1.0 for today, 0.5 after half_life days."""
    if not updated_at:
        return 0.0
    days_ago = (time.time() - updated_at) / 86400
    if days_ago < 0:
        return 1.0
    decay = math.log(2) / RECENCY_HALF_LIFE_DAYS
    return math.exp(-decay * days_ago)


def maturity_score(version_count):
    """Log-scaled maturity: more published versions = more battle-tested."""
    return math.log(max(version_count, 1) + 1)


def composite_score(bm25, pkg):
    """BM25 * (1 + recency_boost + maturity_boost)."""
    recency = RECENCY_WEIGHT * recency_score(pkg.get("updated_at", 0))
    maturity = MATURITY_WEIGHT * maturity_score(pkg.get("version_count", 1))
    return bm25 * (1 + recency + maturity)


def is_compatible(pkg_compiler, user_version_tuple):
    """True if user's Typst version >= package's minimum compiler version."""
    if not pkg_compiler:
        return True
    return user_version_tuple >= parse_version(pkg_compiler)


def filter_by_metadata(packages, name_to_idx, category, discipline):
    """Return set of doc indices matching category/discipline filters."""
    allowed = set(range(len(packages)))

    if category:
        cat_lower = category.lower()
        allowed = {
            name_to_idx[p["name"]]
            for p in packages
            if cat_lower in [c.lower() for c in p.get("categories", [])]
            and p["name"] in name_to_idx
        }

    if discipline:
        disc_lower = discipline.lower()
        disc_match = {
            name_to_idx[p["name"]]
            for p in packages
            if disc_lower in [d.lower() for d in p.get("disciplines", [])]
            and p["name"] in name_to_idx
        }
        allowed = allowed & disc_match

    return allowed


def filter_by_compatibility(packages, name_to_idx, user_version_tuple):
    """Return set of doc indices compatible with user's Typst version."""
    return {
        name_to_idx[p["name"]]
        for p in packages
        if is_compatible(p.get("compiler", ""), user_version_tuple)
        and p["name"] in name_to_idx
    }


def list_values(packages, field):
    """Collect and count unique values for a metadata list field."""
    counts = defaultdict(int)
    for p in packages:
        for val in p.get(field, []):
            counts[val] += 1
    return sorted(counts.items(), key=lambda x: -x[1])


def format_table(results, packages_by_name, doc_names):
    """Format results as a human-readable table."""
    if not results:
        return "No results found."

    lines = []
    lines.append(
        f"{'Name':<28} {'Version':<10} {'Compiler':<10} {'Categories':<20} Description"
    )
    lines.append("-" * 110)

    for doc_idx, score in results:
        name = doc_names[doc_idx]
        pkg = packages_by_name.get(name, {})
        version = pkg.get("version", "?")
        compiler = pkg.get("compiler", "-") or "-"
        cats = ", ".join(pkg.get("categories", [])) or "-"
        desc = pkg.get("description", "")
        if len(desc) > 45:
            desc = desc[:42] + "..."
        lines.append(f"{name:<28} {version:<10} {compiler:<10} {cats:<20} {desc}")

    lines.append("")
    top_name = doc_names[results[0][0]]
    top_pkg = packages_by_name.get(top_name, {})
    top_ver = top_pkg.get("version", "?")
    lines.append(f'Import top result: #import "@preview/{top_name}:{top_ver}": *')

    return "\n".join(lines)


def format_json(results, packages_by_name, doc_names):
    """Format results as JSON."""
    out = []
    for doc_idx, score in results:
        name = doc_names[doc_idx]
        pkg = packages_by_name.get(name, {})
        out.append(
            {
                "name": name,
                "version": pkg.get("version", "?"),
                "description": pkg.get("description", ""),
                "categories": pkg.get("categories", []),
                "disciplines": pkg.get("disciplines", []),
                "compiler": pkg.get("compiler", ""),
                "repository": pkg.get("repository", ""),
                "import": f'#import "@preview/{name}:{pkg.get("version", "?")}"',
                "score": round(score, 4),
            }
        )
    return json.dumps(out, indent=2, ensure_ascii=False)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Search Typst Universe packages using pre-computed BM25 index."
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help='Search query (e.g. "chart plotting visualization")',
    )
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=10,
        help="Number of results to show (default: 10)",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Filter by category (e.g. visualization, cv, thesis)",
    )
    parser.add_argument(
        "--discipline",
        default=None,
        help="Filter by discipline (e.g. mathematics, engineering)",
    )
    parser.add_argument(
        "--typst-version",
        default=None,
        help="Typst compiler version for compatibility filter (auto-detected if omitted)",
    )
    parser.add_argument(
        "--no-compat",
        action="store_true",
        help="Disable compatibility filtering (show all packages regardless of compiler version)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available categories with counts",
    )
    parser.add_argument(
        "--list-disciplines",
        action="store_true",
        help="List all available disciplines with counts",
    )
    parser.add_argument(
        "--index-dir",
        default=None,
        help="Directory containing packages.json and packages-bm25.json",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = resolve_data_dir(args.index_dir)

    pkg_path = os.path.join(data_dir, "packages.json")
    idx_path = os.path.join(data_dir, "packages-bm25.json")

    if not os.path.exists(pkg_path) or not os.path.exists(idx_path):
        print(
            f"Error: data files not found in {data_dir}\n"
            "Run tools/fetch-packages.py first to generate the index.",
            file=sys.stderr,
        )
        sys.exit(1)

    packages = load_json(pkg_path)
    packages_by_name = {p["name"]: p for p in packages}

    if args.list_categories:
        vals = list_values(packages, "categories")
        print(f"{'Category':<24} Count")
        print("-" * 36)
        for val, count in vals:
            print(f"{val:<24} {count}")
        return

    if args.list_disciplines:
        vals = list_values(packages, "disciplines")
        print(f"{'Discipline':<28} Count")
        print("-" * 40)
        for val, count in vals:
            print(f"{val:<28} {count}")
        return

    if not args.query and not args.category and not args.discipline:
        print(
            "Error: provide a search query, --category, or --discipline.",
            file=sys.stderr,
        )
        sys.exit(1)

    index = load_json(idx_path)
    doc_names = index["doc_names"]
    name_to_idx = {name: i for i, name in enumerate(doc_names)}

    # Compatibility filter
    user_version = None
    if not args.no_compat:
        version_str = args.typst_version or detect_typst_version()
        if version_str:
            user_version = parse_version(version_str)

    allowed = filter_by_metadata(packages, name_to_idx, args.category, args.discipline)

    if user_version:
        compatible = filter_by_compatibility(packages, name_to_idx, user_version)
        excluded_count = len(allowed) - len(allowed & compatible)
        allowed = allowed & compatible
    else:
        excluded_count = 0

    if args.query:
        query_tokens = tokenize(args.query)
        if not query_tokens:
            print("Error: query produced no searchable tokens.", file=sys.stderr)
            sys.exit(1)

        bm25_scores = bm25_search(query_tokens, index)

        scored = []
        for idx, bm25 in bm25_scores.items():
            if idx not in allowed or bm25 <= 0:
                continue
            name = doc_names[idx]
            pkg = packages_by_name.get(name, {})
            final = composite_score(bm25, pkg)
            scored.append((idx, final))

        ranked = sorted(scored, key=lambda x: -x[1])
    else:
        ranked = [(idx, 0.0) for idx in sorted(allowed)]

    ranked = ranked[: args.top]

    query_desc = args.query if args.query else "all"

    if args.json_output:
        print(format_json(ranked, packages_by_name, doc_names))
    else:
        header = f'Results for "{query_desc}"'
        if args.category:
            header += f" (category: {args.category})"
        if args.discipline:
            header += f" (discipline: {args.discipline})"
        if user_version:
            version_str = args.typst_version or detect_typst_version()
            header += f" [typst {version_str}, {excluded_count} incompatible hidden]"
        header += f" [{len(ranked)} shown]:"
        print(header)
        print(format_table(ranked, packages_by_name, doc_names))


if __name__ == "__main__":
    main()
