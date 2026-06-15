"""Tests for API and symbol search: BM25, filters, LaTeX aliases.

Uses the real pre-built index in skills/typst/data/.
"""

import importlib.util
import os

import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "skills",
    "typst",
    "scripts",
    "search-api.py",
)
DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "skills",
    "typst",
    "data",
)


def _load_module():
    spec = importlib.util.spec_from_file_location("search_api", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sa = _load_module()


@pytest.fixture(scope="module")
def bm25():
    return sa.load_json(os.path.join(DATA_DIR, "api-bm25.json"))


@pytest.fixture(scope="module")
def api():
    return sa.load_json(os.path.join(DATA_DIR, "api.json"))


@pytest.fixture(scope="module")
def legacy_api():
    return sa.load_json(os.path.join(DATA_DIR, "api-0.14.2.json"))


def _search(query, bm25, api, kind=None, top=10):
    """Run BM25 search with optional kind filter, return list of entry names."""
    tokens = sa.tokenize(query)
    if not tokens:
        return []

    candidate_ids = set(range(len(api)))
    if kind:
        candidate_ids = {i for i in candidate_ids if api[i]["kind"] == kind}

    results = sa.bm25_search(tokens, bm25, top_n=len(api))

    weighted = []
    for doc_id, score in results:
        if doc_id not in candidate_ids:
            continue
        weight = api[doc_id].get("weight", 1.0)
        weighted.append((api[doc_id]["name"], score * weight))
        if len(weighted) >= top * 3:
            break

    weighted.sort(key=lambda x: -x[1])
    return [name for name, _ in weighted[:top]]


def _lookup(name, api):
    """Exact name lookup, return list of matching entries."""
    return [e for e in api if e["name"] == name]


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


class TestTokenizer:
    def test_basic(self):
        assert sa.tokenize("Hello World") == ["hello", "world"]

    def test_keeps_single_char(self):
        assert sa.tokenize("h v") == ["h", "v"]

    def test_splits_punctuation(self):
        assert sa.tokenize("str.position") == ["str", "position"]

    def test_empty(self):
        assert sa.tokenize("") == []


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------


class TestDataIntegrity:
    def test_api_not_empty(self, api):
        assert len(api) > 100

    def test_bm25_not_empty(self, bm25):
        assert bm25["meta"]["num_docs"] > 100

    def test_has_all_kinds(self, api):
        kinds = {e["kind"] for e in api}
        assert kinds >= {"function", "method", "constructor", "type", "symbol"}

    def test_has_categories(self, api):
        cats = {e["category"] for e in api}
        assert "Foundations" in cats
        assert "Layout" in cats
        assert "Math" in cats

    def test_entries_have_required_fields(self, api):
        for e in api[:50]:
            assert "name" in e
            assert "kind" in e
            assert "category" in e
            assert "oneliner" in e

    def test_stable_and_legacy_api_snapshots_are_distinct(self, api, legacy_api):
        stable_entries = {(e["name"], e["kind"], e["category"]) for e in api}
        entries = {(e["name"], e["kind"], e["category"]) for e in legacy_api}

        assert ("asset", "function", "Model") in stable_entries
        assert ("path", "function", "Visualize") in entries


# ---------------------------------------------------------------------------
# Function/method search
# ---------------------------------------------------------------------------


class TestFunctionSearch:
    def test_image(self, bm25, api):
        results = _search("image width", bm25, api, kind="function")
        assert "image" in results[:3]

    def test_heading(self, bm25, api):
        results = _search("heading section", bm25, api, kind="function")
        assert "heading" in results[:3]

    def test_table(self, bm25, api):
        results = _search("table rows columns", bm25, api, kind="function")
        assert "table" in results[:3]

    def test_page(self, bm25, api):
        results = _search("page margin paper", bm25, api, kind="function")
        assert "page" in results[:3]

    def test_query(self, bm25, api):
        results = _search("query find elements", bm25, api, kind="function")
        assert "query" in results[:5]

    def test_metadata(self, bm25, api):
        results = _search("metadata value invisible", bm25, api, kind="function")
        assert "metadata" in results[:5]


class TestMethodSearch:
    def test_str_position(self, bm25, api):
        results = _search("string position index", bm25, api, kind="method")
        assert "str.position" in results[:5]

    def test_str_slice(self, bm25, api):
        results = _search("string slice substring", bm25, api, kind="method")
        assert "str.slice" in results[:5]

    def test_content_fields(self, bm25, api):
        results = _search("content fields", bm25, api, kind="method")
        assert "content.fields" in results[:5]

    def test_content_func(self, bm25, api):
        results = _search("content func element", bm25, api, kind="method")
        assert "content.func" in results[:5]

    def test_counter_step(self, bm25, api):
        results = _search("counter step increase", bm25, api, kind="method")
        assert "counter.step" in results[:5]

    def test_color_lighten(self, bm25, api):
        results = _search("color lighten", bm25, api, kind="method")
        assert "color.lighten" in results[:3]


class TestTypeSearch:
    def test_color_type(self, bm25, api):
        results = _search("color", bm25, api, kind="type")
        assert "color" in results[:3]

    def test_alignment_type(self, bm25, api):
        results = _search("alignment", bm25, api, kind="type")
        assert "alignment" in results[:3]


class TestEnumValueSearch:
    def test_pixelated(self, bm25, api):
        """Enum value on image scaling parameter."""
        results = _search("pixelated", bm25, api)
        assert "image" in results[:3]

    def test_cover(self, bm25, api):
        """Enum value on image fit parameter."""
        results = _search("cover fit", bm25, api)
        assert "image" in results[:5]


class TestSingleCharSearch:
    def test_h_function(self, bm25, api):
        results = _search("h", bm25, api, kind="function")
        assert "h" in results[:3]

    def test_v_function(self, bm25, api):
        results = _search("v", bm25, api, kind="function")
        assert "v" in results[:3]


# ---------------------------------------------------------------------------
# Symbol search
# ---------------------------------------------------------------------------


class TestSymbolSearch:
    def test_arrow_right(self, bm25, api):
        results = _search("arrow right", bm25, api, kind="symbol")
        assert "sym.arrow.r" in results[:3]

    def test_arrow_left_double(self, bm25, api):
        results = _search("arrow left double", bm25, api, kind="symbol")
        assert "sym.arrow.l.double" in results[:5]

    def test_arrow_bottom_left(self, bm25, api):
        results = _search("bottom left arrow", bm25, api, kind="symbol")
        assert "sym.arrow.bl" in results[:5]

    def test_integral(self, bm25, api):
        results = _search("integral", bm25, api, kind="symbol")
        assert "sym.integral" in results[:3]

    def test_alpha(self, bm25, api):
        results = _search("alpha", bm25, api, kind="symbol")
        assert "sym.alpha" in results[:3]

    def test_clockwise(self, bm25, api):
        results = _search("clockwise", bm25, api, kind="symbol")
        assert "sym.arrow.cw" in results[:5]


# ---------------------------------------------------------------------------
# LaTeX alias search
# ---------------------------------------------------------------------------


class TestLatexAliases:
    def test_rightarrow(self, bm25, api):
        results = _search("rightarrow", bm25, api, kind="symbol")
        assert "sym.arrow.r" in results[:3]

    def test_leftarrow(self, bm25, api):
        results = _search("leftarrow", bm25, api, kind="symbol")
        assert "sym.arrow.l" in results[:3]

    def test_leq(self, bm25, api):
        results = _search("leq", bm25, api, kind="symbol")
        assert "sym.lt.eq" in results[:3]

    def test_geq(self, bm25, api):
        results = _search("geq", bm25, api, kind="symbol")
        assert "sym.gt.eq" in results[:3]

    def test_infty(self, bm25, api):
        results = _search("infty", bm25, api, kind="symbol")
        assert "sym.infinity" in results[:3]

    def test_pm(self, bm25, api):
        results = _search("pm", bm25, api, kind="symbol")
        assert "sym.plus.minus" in results[:5]

    def test_cdot(self, bm25, api):
        results = _search("cdot", bm25, api, kind="symbol")
        assert "sym.dot.op" in results[:5]

    def test_partial(self, bm25, api):
        results = _search("partial", bm25, api, kind="symbol")
        assert "sym.partial" in results[:3]

    def test_forall(self, bm25, api):
        results = _search("forall", bm25, api, kind="symbol")
        assert "sym.forall" in results[:3]

    def test_int_finds_integral(self, bm25, api):
        results = _search("int", bm25, api, kind="symbol")
        assert "sym.integral" in results[:5]


# ---------------------------------------------------------------------------
# Exact name lookup
# ---------------------------------------------------------------------------


class TestExactLookup:
    def test_str_position(self, api):
        matches = _lookup("str.position", api)
        assert len(matches) == 1
        assert matches[0]["kind"] == "method"
        assert "int" in matches[0]["returns"]

    def test_image(self, api):
        matches = _lookup("image", api)
        assert len(matches) == 1
        param_names = [p["name"] for p in matches[0]["params"]]
        assert "width" in param_names
        assert "height" in param_names

    def test_heading(self, api):
        matches = _lookup("heading", api)
        assert len(matches) == 1
        param_names = [p["name"] for p in matches[0]["params"]]
        assert "level" in param_names

    def test_symbol_lookup(self, api):
        matches = _lookup("sym.arrow.r", api)
        assert len(matches) >= 1
        assert matches[0]["kind"] == "symbol"
        assert matches[0]["value"] == "→"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_no_results(self, bm25, api):
        results = _search("zzzznotawordxyz", bm25, api)
        assert results == []

    def test_empty_query(self, bm25, api):
        results = _search("", bm25, api)
        assert results == []

    def test_nonexistent_name(self, api):
        matches = _lookup("nonexistent.function.xyz", api)
        assert matches == []

    def test_kind_filter_reduces(self, bm25, api):
        all_results = _search("color", bm25, api, top=50)
        method_only = _search("color", bm25, api, kind="method", top=50)
        assert len(method_only) < len(all_results)
