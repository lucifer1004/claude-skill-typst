"""Tests for package search: BM25, composite scoring, compatibility filtering.

Uses the real pre-built index in skills/typst/data/.
"""

import importlib.util
import math
import os
import time

import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "skills",
    "typst",
    "scripts",
    "search-packages.py",
)
DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "skills",
    "typst",
    "data",
)


def _load_module():
    spec = importlib.util.spec_from_file_location("search_packages", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sp = _load_module()


@pytest.fixture(scope="module")
def index():
    return sp.load_json(os.path.join(DATA_DIR, "packages-bm25.json"))


@pytest.fixture(scope="module")
def packages():
    return sp.load_json(os.path.join(DATA_DIR, "packages.json"))


@pytest.fixture(scope="module")
def packages_by_name(packages):
    return {p["name"]: p for p in packages}


@pytest.fixture(scope="module")
def name_to_idx(index):
    return {name: i for i, name in enumerate(index["doc_names"])}


def _search(query, index, packages, packages_by_name, top=10):
    tokens = sp.tokenize(query)
    bm25_scores = sp.bm25_search(tokens, index)
    scored = []
    for idx, bm25 in bm25_scores.items():
        if bm25 <= 0:
            continue
        name = index["doc_names"][idx]
        pkg = packages_by_name.get(name, {})
        final = sp.composite_score(bm25, pkg)
        scored.append((name, final))
    return [name for name, _ in sorted(scored, key=lambda x: -x[1])[:top]]


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


class TestTokenizer:
    def test_basic(self):
        assert sp.tokenize("Hello World") == ["hello", "world"]

    def test_drops_short(self):
        assert sp.tokenize("a bb c dd") == ["bb", "dd"]

    def test_splits_punctuation(self):
        assert sp.tokenize("foo-bar_baz.qux") == ["foo", "bar", "baz", "qux"]

    def test_empty(self):
        assert sp.tokenize("") == []
        assert sp.tokenize("  - ! ") == []


# ---------------------------------------------------------------------------
# Version parsing
# ---------------------------------------------------------------------------


class TestParseVersion:
    def test_full(self):
        assert sp.parse_version("0.13.1") == (0, 13, 1)

    def test_short(self):
        assert sp.parse_version("1.2") == (1, 2, 0)

    def test_empty(self):
        assert sp.parse_version("") == (0, 0, 0)
        assert sp.parse_version(None) == (0, 0, 0)

    def test_ordering(self):
        assert sp.parse_version("0.13.0") < sp.parse_version("0.13.1")
        assert sp.parse_version("0.14.0") > sp.parse_version("0.13.1")
        assert sp.parse_version("1.0.0") > sp.parse_version("0.99.99")


# ---------------------------------------------------------------------------
# Compatibility
# ---------------------------------------------------------------------------


class TestCompatibility:
    def test_no_compiler_always_compatible(self):
        assert sp.is_compatible("", (0, 1, 0))
        assert sp.is_compatible(None, (0, 1, 0))

    def test_exact_match(self):
        assert sp.is_compatible("0.13.0", (0, 13, 0))

    def test_newer_user(self):
        assert sp.is_compatible("0.13.0", (0, 14, 0))

    def test_older_user(self):
        assert not sp.is_compatible("0.14.0", (0, 13, 0))


# ---------------------------------------------------------------------------
# Scoring components
# ---------------------------------------------------------------------------


class TestRecencyScore:
    def test_now_is_one(self):
        score = sp.recency_score(time.time())
        assert score > 0.99

    def test_future_is_one(self):
        assert sp.recency_score(time.time() + 86400) == 1.0

    def test_old_is_low(self):
        two_years_ago = time.time() - 2 * 365 * 86400
        score = sp.recency_score(two_years_ago)
        assert score < 0.3

    def test_zero_is_zero(self):
        assert sp.recency_score(0) == 0.0

    def test_half_life(self):
        one_year_ago = time.time() - 365 * 86400
        score = sp.recency_score(one_year_ago)
        assert 0.45 < score < 0.55

    def test_monotonic(self):
        now = time.time()
        scores = [sp.recency_score(now - d * 86400) for d in [0, 30, 90, 365, 730]]
        assert scores == sorted(scores, reverse=True)


class TestMaturityScore:
    def test_one_version(self):
        assert sp.maturity_score(1) == math.log(2)

    def test_increases_with_count(self):
        assert sp.maturity_score(10) > sp.maturity_score(1)
        assert sp.maturity_score(20) > sp.maturity_score(10)

    def test_sublinear(self):
        jump_1_to_10 = sp.maturity_score(10) - sp.maturity_score(1)
        jump_10_to_20 = sp.maturity_score(20) - sp.maturity_score(10)
        assert jump_1_to_10 > jump_10_to_20

    def test_zero_handled(self):
        assert sp.maturity_score(0) > 0


class TestCompositeScore:
    def test_boost_above_bm25(self):
        pkg = {"updated_at": time.time(), "version_count": 10}
        assert sp.composite_score(10.0, pkg) > 10.0

    def test_empty_pkg_still_boosts(self):
        assert sp.composite_score(10.0, {}) > 10.0

    def test_zero_bm25_stays_zero(self):
        pkg = {"updated_at": time.time(), "version_count": 20}
        assert sp.composite_score(0.0, pkg) == 0.0


# ---------------------------------------------------------------------------
# BM25 search (real index)
# ---------------------------------------------------------------------------


class TestBM25Search:
    def test_returns_scores(self, index):
        scores = sp.bm25_search(["draw"], index)
        assert len(scores) > 0
        assert all(s > 0 for s in scores.values())

    def test_unknown_term_empty(self, index):
        scores = sp.bm25_search(["zzzznotaword"], index)
        assert len(scores) == 0

    def test_multi_term_higher(self, index):
        s1 = sp.bm25_search(["draw"], index)
        s2 = sp.bm25_search(["draw", "canvas"], index)
        common = set(s1) & set(s2)
        assert all(s2[k] >= s1[k] for k in common)


# ---------------------------------------------------------------------------
# Typical searches (real index, composite scoring)
# ---------------------------------------------------------------------------


class TestTypicalSearches:
    def test_drawing(self, index, packages, packages_by_name):
        results = _search("drawing canvas vector", index, packages, packages_by_name)
        assert "cetz" in results[:3]

    def test_presentation(self, index, packages, packages_by_name):
        results = _search("presentation slides", index, packages, packages_by_name)
        top5 = results[:5]
        assert any(p in top5 for p in ["touying", "polylux", "typslides"])

    def test_theorem(self, index, packages, packages_by_name):
        results = _search("theorem proof lemma", index, packages, packages_by_name)
        has_theorem_pkg = any(
            "theorem" in r or "thm" in r or "proof" in r for r in results[:5]
        )
        assert has_theorem_pkg

    def test_chart_plot(self, index, packages, packages_by_name):
        results = _search("chart plot data", index, packages, packages_by_name)
        top10 = results[:10]
        assert any(p in top10 for p in ["cetz-plot", "lilaq", "primaviz"])

    def test_cv_resume(self, index, packages, packages_by_name):
        results = _search("resume curriculum vitae", index, packages, packages_by_name)
        assert len(results) > 0

    def test_diagram_flowchart(self, index, packages, packages_by_name):
        results = _search("diagram flowchart arrow", index, packages, packages_by_name)
        assert "fletcher" in results[:5]

    def test_code_highlighting(self, index, packages, packages_by_name):
        results = _search(
            "code formatting line numbers", index, packages, packages_by_name
        )
        top10 = results[:10]
        assert any(p in top10 for p in ["codly", "codelst", "zebraw"])


# ---------------------------------------------------------------------------
# Filters (real index)
# ---------------------------------------------------------------------------


class TestFilters:
    def test_category_filter(self, packages, name_to_idx):
        allowed = sp.filter_by_metadata(packages, name_to_idx, "cv", None)
        assert len(allowed) > 0
        for idx in allowed:
            name = [n for n, i in name_to_idx.items() if i == idx][0]
            pkg = next(p for p in packages if p["name"] == name)
            assert "cv" in [c.lower() for c in pkg["categories"]]

    def test_discipline_filter(self, packages, name_to_idx):
        allowed = sp.filter_by_metadata(packages, name_to_idx, None, "mathematics")
        assert len(allowed) > 0

    def test_combined_filter(self, packages, name_to_idx):
        cat_only = sp.filter_by_metadata(packages, name_to_idx, "visualization", None)
        combined = sp.filter_by_metadata(
            packages, name_to_idx, "visualization", "mathematics"
        )
        assert combined <= cat_only

    def test_compatibility_filter(self, packages, name_to_idx):
        old = sp.filter_by_compatibility(packages, name_to_idx, (0, 11, 0))
        new = sp.filter_by_compatibility(packages, name_to_idx, (99, 0, 0))
        assert old < new

    def test_compat_excludes_newer(self, packages, name_to_idx, packages_by_name):
        user_v = (0, 12, 0)
        compatible = sp.filter_by_compatibility(packages, name_to_idx, user_v)
        for idx in compatible:
            name = [n for n, i in name_to_idx.items() if i == idx][0]
            pkg = packages_by_name[name]
            compiler = pkg.get("compiler", "")
            if compiler:
                assert sp.parse_version(compiler) <= user_v
