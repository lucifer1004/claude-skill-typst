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
        path.relative_to(SKILL_DIR).as_posix()
        for path in SKILL_DIR.rglob("*.md")
        if path.name != "SKILL.md"
        and "agents" not in path.relative_to(SKILL_DIR).parts
        and "examples" not in path.relative_to(SKILL_DIR).parts
    )


def _linked_markdown_docs():
    text = SKILL_FILE.read_text(encoding="utf-8")
    return {
        Path(target).as_posix()
        for target in re.findall(r"\[[^\]]+\]\(([^)#]+\.md)\)", text)
    }


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


def test_cli_guide_is_routed_and_adds_workflow_guidance():
    linked_docs = _linked_markdown_docs()
    cli_path = SKILL_DIR / "cli.md"

    assert "cli.md" in linked_docs
    assert cli_path.exists()

    text = cli_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 80

    for expected in [
        "What This Adds",
        "Command Choice",
        "CI Export Recipe",
        "PDF Standards",
        "Template Init",
        "Gotchas",
        "not a mirror",
        "[debug.md](debug.md)",
        "[query.md](query.md)",
        "[basics.md](basics.md)",
        "[styling.md](styling.md)",
        "[perf.md](perf.md)",
        "[package.md](package.md)",
        "typst init",
        "--pdf-standard",
        "--deps",
        "--package-cache-path",
        "--creation-timestamp",
    ]:
        assert expected in text


def test_query_options_table_has_valid_format_row():
    text = (SKILL_DIR / "query.md").read_text(encoding="utf-8")

    assert "| `--format json\\|yaml` |" in text
    assert "| \\`--format json" not in text
    assert "| yaml\\`" not in text


def test_verify_agent_allows_element_selector_queries_without_metadata():
    text = (SKILL_DIR / "agents" / "typst-verify.md").read_text(encoding="utf-8")

    assert "Element selectors do not require `metadata()`" in text
    assert "the document must contain `metadata()` elements" not in text
