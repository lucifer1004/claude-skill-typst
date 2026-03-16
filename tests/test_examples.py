"""Tests for Typst code examples: standalone .typ files and inline doc snippets.

Validates that:
1. All .typ example files compile with `typst compile`
2. All inline ```typst code blocks in .md docs compile (with a variable preamble)

Requires: typst CLI in PATH, markdown-it-py
"""

import importlib.util
import os
import shutil
import subprocess
import tempfile

import pytest
from markdown_it import MarkdownIt

SKILL_DIR = os.path.join(os.path.dirname(__file__), "..", "skills", "typst")
EXAMPLES_DIR = os.path.join(SKILL_DIR, "examples")
SCRIPT_PATH = os.path.join(SKILL_DIR, "scripts", "validate-examples.py")

# Load validate-examples module for its constants
_spec = importlib.util.spec_from_file_location("validate_examples", SCRIPT_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

PREAMBLE = _mod.PREAMBLE
SKIP_PATTERNS = _mod.SKIP_PATTERNS
should_skip = _mod.should_skip

HAS_TYPST = shutil.which("typst") is not None


def _compile_typst(path):
    """Compile a .typ file and return (success, stderr)."""
    result = subprocess.run(
        ["typst", "compile", path, "/dev/null", "-f", "pdf"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return result.returncode == 0, result.stderr.strip()


def _compile_snippet(code, preamble=True):
    """Compile a Typst code snippet and return (success, stderr)."""
    full_code = (PREAMBLE + "\n" + code) if preamble else code
    with tempfile.NamedTemporaryFile(
        suffix=".typ", mode="w", delete=True, dir=SKILL_DIR
    ) as f:
        f.write(full_code)
        f.flush()
        return _compile_typst(f.name)


# ---------------------------------------------------------------------------
# Standalone .typ example files
# ---------------------------------------------------------------------------


def _collect_typ_files():
    """Collect all .typ files in the examples directory."""
    files = []
    for root, _dirs, filenames in os.walk(EXAMPLES_DIR):
        for name in filenames:
            if name.endswith(".typ"):
                files.append(os.path.join(root, name))
    return sorted(files)


@pytest.mark.skipif(not HAS_TYPST, reason="typst CLI not in PATH")
@pytest.mark.parametrize(
    "typ_file",
    _collect_typ_files(),
    ids=lambda p: os.path.relpath(p, EXAMPLES_DIR),
)
def test_example_compiles(typ_file):
    ok, stderr = _compile_typst(typ_file)
    assert ok, f"Failed to compile {typ_file}:\n{stderr}"


# ---------------------------------------------------------------------------
# Inline ```typst code blocks from .md docs
# ---------------------------------------------------------------------------


def _collect_inline_blocks():
    """Extract all ```typst blocks from .md files, returning (id, code) pairs."""
    md = MarkdownIt()
    blocks = []
    for name in sorted(os.listdir(SKILL_DIR)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(SKILL_DIR, name)
        with open(path) as f:
            text = f.read()
        for token in md.parse(text):
            if token.type == "fence" and token.info.strip() == "typst":
                line = token.map[0] + 2
                block_id = f"{name}:{line}"
                blocks.append((block_id, token.content))
    return blocks


_ALL_BLOCKS = _collect_inline_blocks()
_COMPILABLE = [(bid, code) for bid, code in _ALL_BLOCKS if should_skip(code) is None]
_SKIPPED = [(bid, code) for bid, code in _ALL_BLOCKS if should_skip(code) is not None]


@pytest.mark.skipif(not HAS_TYPST, reason="typst CLI not in PATH")
@pytest.mark.parametrize("block_id,code", _COMPILABLE, ids=lambda *a: a[0])
def test_inline_block_compiles(block_id, code):
    ok, stderr = _compile_snippet(code)
    assert ok, f"Inline block {block_id} failed:\n{stderr}"


def test_no_blocks_lost():
    """Ensure skip + compilable == total (no blocks silently dropped)."""
    assert len(_COMPILABLE) + len(_SKIPPED) == len(_ALL_BLOCKS)


def test_block_count_sanity():
    """Ensure we found a reasonable number of blocks (catch extraction regressions)."""
    assert len(_ALL_BLOCKS) >= 100, (
        f"Expected >= 100 inline typst blocks, found {len(_ALL_BLOCKS)}"
    )


@pytest.mark.skipif(not HAS_TYPST, reason="typst CLI not in PATH")
def test_preamble_compiles():
    """Ensure the injected preamble itself is valid Typst."""
    ok, stderr = _compile_snippet("", preamble=True)
    assert ok, f"Preamble alone failed to compile:\n{stderr}"


@pytest.mark.skipif(not HAS_TYPST, reason="typst CLI not in PATH")
def test_skipped_blocks_are_genuinely_problematic():
    """Verify that at least some skipped blocks actually fail without skip protection."""
    failures = 0
    sample = _SKIPPED[:10]
    for _bid, code in sample:
        ok, _stderr = _compile_snippet(code)
        if not ok:
            failures += 1
    assert failures > 0, "No skipped blocks failed — skip patterns may be too broad"
