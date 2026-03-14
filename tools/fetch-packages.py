#!/usr/bin/env python3
"""Fetch Typst Universe package index and build BM25 search index.

Downloads the canonical package list from packages.typst.org, deduplicates
to latest version per package, and writes:
  - packages.json     (minimal metadata for display)
  - packages-bm25.json (pre-computed inverted index for search)

This is a dev/CI tool, NOT part of the distributed skill bundle.
"""

import argparse
import json
import math
import os
import re
import urllib.request
from collections import defaultdict

INDEX_URL = "https://packages.typst.org/preview/index.json"

NAME_BOOST = 3
KEYWORD_BOOST = 2
DESCRIPTION_BOOST = 1

BM25_K1 = 1.5
BM25_B = 0.75


def tokenize(text):
    """Lowercase, split on non-alphanumeric, drop tokens <= 1 char."""
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 1]


def fetch_index(url):
    print(f"Fetching {url} ...")
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    print(f"  Got {len(data)} entries")
    return data


def deduplicate(entries):
    """Keep only the latest version per package, tracking version count."""
    by_name = defaultdict(list)
    for entry in entries:
        by_name[entry["name"]].append(entry)

    latest = []
    for name in sorted(by_name):
        versions = by_name[name]
        versions.sort(key=lambda p: _version_tuple(p["version"]))
        best = versions[-1]
        best["_version_count"] = len(versions)
        latest.append(best)

    print(f"  Deduplicated to {len(latest)} unique packages")
    return latest


def _version_tuple(v):
    parts = []
    for seg in v.split("."):
        try:
            parts.append(int(seg))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def build_packages_json(entries):
    """Extract metadata for display and scoring."""
    packages = []
    for e in entries:
        packages.append(
            {
                "name": e["name"],
                "version": e["version"],
                "description": e.get("description", ""),
                "keywords": e.get("keywords", []),
                "categories": e.get("categories", []),
                "disciplines": e.get("disciplines", []),
                "repository": e.get("repository", ""),
                "compiler": e.get("compiler", ""),
                "updated_at": e.get("updatedAt", 0),
                "version_count": e.get("_version_count", 1),
            }
        )
    return packages


def build_virtual_document(pkg):
    """Build a token list with field boosting baked in."""
    tokens = []
    tokens.extend(tokenize(pkg["name"]) * NAME_BOOST)
    for kw in pkg.get("keywords", []):
        tokens.extend(tokenize(kw) * KEYWORD_BOOST)
    tokens.extend(tokenize(pkg.get("description", "")) * DESCRIPTION_BOOST)
    return tokens


def build_bm25_index(packages):
    """Build inverted index with IDF weights from package list."""
    num_docs = len(packages)
    doc_names = []
    doc_lengths = []
    tf_per_doc = []

    for pkg in packages:
        doc_names.append(pkg["name"])
        tokens = build_virtual_document(pkg)
        doc_lengths.append(len(tokens))

        tf = defaultdict(int)
        for tok in tokens:
            tf[tok] += 1
        tf_per_doc.append(tf)

    avg_dl = sum(doc_lengths) / num_docs if num_docs else 0

    df = defaultdict(int)
    for tf in tf_per_doc:
        for term in tf:
            df[term] += 1

    idf = {}
    for term, freq in df.items():
        idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1)

    postings = defaultdict(list)
    for doc_idx, tf in enumerate(tf_per_doc):
        for term, freq in tf.items():
            postings[term].append([doc_idx, freq])

    index = {
        "meta": {
            "num_docs": num_docs,
            "avg_dl": round(avg_dl, 2),
            "k1": BM25_K1,
            "b": BM25_B,
        },
        "idf": {t: round(v, 4) for t, v in sorted(idf.items())},
        "postings": dict(sorted(postings.items())),
        "doc_lengths": doc_lengths,
        "doc_names": doc_names,
    }

    num_terms = len(idf)
    num_postings = sum(len(v) for v in postings.values())
    print(f"  BM25 index: {num_terms} terms, {num_postings} postings")
    return index


def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = os.path.getsize(path) / 1024
    print(f"  Wrote {path} ({size_kb:.1f} KB)")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch Typst package index and build BM25 search index."
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for data files (default: skills/typst/data/ relative to repo root)",
    )
    parser.add_argument(
        "--url",
        default=INDEX_URL,
        help=f"Package index URL (default: {INDEX_URL})",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.output_dir:
        output_dir = args.output_dir
    else:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(repo_root, "skills", "typst", "data")

    entries = fetch_index(args.url)
    latest = deduplicate(entries)
    packages = build_packages_json(latest)
    bm25_index = build_bm25_index(packages)

    pkg_path = os.path.join(output_dir, "packages.json")
    idx_path = os.path.join(output_dir, "packages-bm25.json")

    write_json(packages, pkg_path)
    write_json(bm25_index, idx_path)

    print(f"\nDone. {len(packages)} packages indexed.")


if __name__ == "__main__":
    main()
