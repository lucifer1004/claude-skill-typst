"""Structure tests for the bundled Typst skill.

These checks enforce the published-skill boundary:
1. `SKILL.md` is the single bundled entry point.
2. Every bundled `.md` doc is reachable from `SKILL.md`.
"""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "typst"
SKILL_FILE = SKILL_DIR / "SKILL.md"


def _bundled_markdown_docs():
    return sorted(
        path.name for path in SKILL_DIR.glob("*.md") if path.name != "SKILL.md"
    )


def _linked_markdown_docs():
    text = SKILL_FILE.read_text(encoding="utf-8")
    return {Path(target).name for target in re.findall(r"\[[^\]]+\]\(([^)#]+\.md)\)", text)}


def test_bundled_skill_has_no_readme():
    assert not (SKILL_DIR / "README.md").exists(), (
        "Bundled skill should keep SKILL.md as its only entry point; "
        "move human-facing README content to the repository root."
    )


def test_all_bundled_markdown_docs_are_routed_from_skill():
    bundled_docs = set(_bundled_markdown_docs())
    linked_docs = _linked_markdown_docs()
    missing = sorted(bundled_docs - linked_docs)
    assert not missing, (
        "Bundled markdown docs must be discoverable from SKILL.md. "
        f"Missing routes for: {', '.join(missing)}"
    )
