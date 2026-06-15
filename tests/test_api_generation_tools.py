"""Tests for API generation and channel-aware search helpers."""

import importlib.util
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
FETCH_SCRIPT = os.path.join(ROOT, "tools", "fetch-api-docs.py")
SEARCH_SCRIPT = os.path.join(ROOT, "skills", "typst", "scripts", "search-api.py")


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_fetch_api_docs_writes_custom_stem_from_normalized_entries(
    tmp_path, monkeypatch
):
    fetch_api_docs = _load_module("fetch_api_docs", FETCH_SCRIPT)
    input_path = tmp_path / "entries.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "name": "image",
                    "category": "Visualize",
                    "kind": "function",
                    "oneliner": "Embeds an image.",
                    "params": [{"name": "path", "types": ["str"], "required": True}],
                    "returns": ["content"],
                    "route": "/reference/visualize/image/",
                    "weight": 1.5,
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(fetch_api_docs, "fetch_latex_aliases", lambda: {})
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "fetch-api-docs.py",
            str(input_path),
            "--input-format",
            "entries",
            "--output-stem",
            "api-main",
            "--out-dir",
            str(tmp_path),
        ],
    )

    fetch_api_docs.main()

    api_path = tmp_path / "api-main.json"
    bm25_path = tmp_path / "api-main-bm25.json"
    assert api_path.exists()
    assert bm25_path.exists()
    assert not (tmp_path / "api.json").exists()
    assert json.loads(api_path.read_text(encoding="utf-8"))[0]["name"] == "image"
    assert json.loads(bm25_path.read_text(encoding="utf-8"))["meta"]["num_docs"] == 1


def test_search_api_resolves_stable_legacy_and_main_channel_paths(tmp_path):
    search_api = _load_module("search_api", SEARCH_SCRIPT)

    assert search_api.resolve_index_paths(str(tmp_path), "stable") == (
        os.path.join(str(tmp_path), "api.json"),
        os.path.join(str(tmp_path), "api-bm25.json"),
    )
    assert search_api.resolve_index_paths(str(tmp_path), "0.14.2") == (
        os.path.join(str(tmp_path), "api-0.14.2.json"),
        os.path.join(str(tmp_path), "api-0.14.2-bm25.json"),
    )
    assert search_api.resolve_index_paths(str(tmp_path), "main") == (
        os.path.join(str(tmp_path), "api-main.json"),
        os.path.join(str(tmp_path), "api-main-bm25.json"),
    )


def test_typst_main_exporter_template_exists():
    exporter_path = os.path.join(ROOT, "tools", "typst-api-exporter.rs")

    with open(exporter_path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "struct ApiEntry" in source
    assert "Library::builder().with_features(Features::all()).build()" in source
    assert "write_entries" in source


def test_update_api_workflow_generates_main_channel_only():
    workflow_path = os.path.join(ROOT, ".github", "workflows", "update-api.yml")

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = f.read()

    assert "tools/typst-api-exporter.rs" in workflow
    assert "--input-format entries" in workflow
    assert "--output-stem api-main" in workflow
    assert "skills/typst/data/api-main.json" in workflow
    assert "skills/typst/data/api.json" not in workflow
