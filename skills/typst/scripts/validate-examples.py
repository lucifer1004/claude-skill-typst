#!/usr/bin/env python3
"""Extract and validate inline Typst code blocks from skill documentation.

Extracts ```typst fenced code blocks from .md files using a CommonMark parser,
wraps snippets with a standard preamble to supply common undefined variables,
and attempts to compile each block with `typst compile`.

Requires: markdown-it-py (pip install markdown-it-py)

Usage:
    python3 scripts/validate-examples.py                    # validate all .md files
    python3 scripts/validate-examples.py basics.md types.md # specific files
    python3 scripts/validate-examples.py --json             # JSON output
    python3 scripts/validate-examples.py --keep             # keep temp files for debugging
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from markdown_it import MarkdownIt
except ImportError:
    print(
        "ERROR: markdown-it-py is required. Install with: pip install markdown-it-py",
        file=sys.stderr,
    )
    sys.exit(2)

# Standard preamble injected before each snippet to define common variables
# used across documentation examples.
PREAMBLE = r"""
// === Validation preamble (auto-injected) ===
#let items = ("alpha", "beta", "gamma")
#let condition = true
#let x = 5
#let config = (color: blue, size: 12pt, name: "test")
#let dict = (name: "Alice", age: 30, city: "NYC")
#let key = "name"
#let default = "N/A"
#let body = [Sample body content]
#let prefix = [Pre]
#let suffix = [Suf]
#let prefix-str = "Pre"
#let body-str = "Body"
#let suffix-str = "Suf"
#let transform(x) = x
// === End preamble ===
"""

# Patterns that indicate a block is intentionally non-compilable
SKIP_PATTERNS = [
    r"^\s*//\s*\.\.\.",  # // ... placeholder
    r"\.\.\.",  # any ... ellipsis
    r'#import\s+"[^@]',  # relative imports (file not present)
    r'#import\s+"@local/',  # local packages (not installed)
    r'#import\s+"@preview/package-name',  # placeholder package names
    r'#include\s+"',  # include (file not present)
    r"image\(",  # image() references (with or without #)
    r"#bibliography\(",  # bibliography references
    r"#read\(",  # read() file references
    r"#csv\(",  # csv() file references
    r"#json\(",  # json() file references but allow xml()
    r"#yaml\(",  # yaml() file references
    r'#raw\("',  # raw() with string (often partial)
    r"item\.key",  # assumes dict-shaped items
    r"```xml",  # embedded raw XML blocks
    r"@\w+\d{4}",  # citation references (require .bib file)
]


def extract_blocks(md_path: Path) -> list[dict]:
    """Extract ```typst code blocks with line numbers using CommonMark parsing."""
    text = md_path.read_text()
    md = MarkdownIt()
    tokens = md.parse(text)
    blocks = []

    for token in tokens:
        if token.type == "fence" and token.info.strip() == "typst":
            # token.map is [start_line, end_line] (0-indexed)
            # Content starts on the line after the opening fence
            line = token.map[0] + 2  # +1 for 0-index, +1 for fence line
            blocks.append(
                {
                    "file": str(md_path),
                    "line": line,
                    "code": token.content,
                }
            )

    return blocks


def should_skip(code: str) -> str | None:
    """Return a reason string if this block should be skipped, else None."""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, code):
            return f"matches skip pattern: {pattern}"
    return None


def compile_block(
    code: str, preamble: bool = True, keep: bool = False
) -> tuple[bool, str]:
    """Try to compile a Typst code block. Returns (success, stderr)."""
    full_code = (PREAMBLE + "\n" + code) if preamble else code

    with tempfile.NamedTemporaryFile(
        suffix=".typ", mode="w", delete=not keep, dir="."
    ) as f:
        f.write(full_code)
        f.flush()
        tmp_path = f.name

        try:
            result = subprocess.run(
                ["typst", "compile", tmp_path, "/dev/null", "-f", "pdf"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0, result.stderr.strip()
        except FileNotFoundError:
            return False, "typst not found in PATH"
        except subprocess.TimeoutExpired:
            return False, "compilation timed out (10s)"


def main():
    parser = argparse.ArgumentParser(
        description="Validate inline Typst examples from skill .md files",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific .md files to validate (default: all *.md in skill dir)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep temporary .typ files for debugging",
    )
    parser.add_argument(
        "--no-preamble",
        action="store_true",
        help="Skip injecting the standard variable preamble",
    )
    parser.add_argument(
        "--include-skipped",
        action="store_true",
        help="Also attempt to compile blocks that would normally be skipped",
    )
    args = parser.parse_args()

    # Resolve skill directory
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent

    if args.files:
        md_files = [skill_dir / f for f in args.files]
    else:
        md_files = sorted(skill_dir.glob("*.md"))

    results = []
    counts = {"pass": 0, "fail": 0, "skip": 0}

    for md_file in md_files:
        if not md_file.exists():
            print(f"WARNING: {md_file} not found, skipping", file=sys.stderr)
            continue

        blocks = extract_blocks(md_file)
        for block in blocks:
            skip_reason = should_skip(block["code"])
            rel_path = md_file.name

            if skip_reason and not args.include_skipped:
                counts["skip"] += 1
                results.append(
                    {
                        "file": rel_path,
                        "line": block["line"],
                        "status": "skip",
                        "reason": skip_reason,
                    }
                )
                continue

            ok, stderr = compile_block(
                block["code"],
                preamble=not args.no_preamble,
                keep=args.keep,
            )

            if ok:
                counts["pass"] += 1
                status = "pass"
            else:
                counts["fail"] += 1
                status = "fail"

            entry = {
                "file": rel_path,
                "line": block["line"],
                "status": status,
            }
            if not ok:
                # Show first line of error for context
                first_error = stderr.split("\n")[0] if stderr else "unknown error"
                entry["error"] = first_error
            results.append(entry)

    # Output
    if args.json_output:
        print(json.dumps({"counts": counts, "results": results}, indent=2))
    else:
        for r in results:
            icon = {"pass": "OK", "fail": "FAIL", "skip": "SKIP"}[r["status"]]
            loc = f"{r['file']}:{r['line']}"
            msg = r.get("error", r.get("reason", ""))
            suffix = f"  {msg}" if msg else ""
            print(f"{icon:>4}  {loc:<30}{suffix}")

        print()
        total = counts["pass"] + counts["fail"] + counts["skip"]
        print(
            f"Total: {total}  Pass: {counts['pass']}  Fail: {counts['fail']}  Skip: {counts['skip']}"
        )

    sys.exit(1 if counts["fail"] > 0 else 0)


if __name__ == "__main__":
    main()
