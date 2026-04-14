# claude-skill-typst task runner

set dotenv-load := false

# List available recipes
[private]
default:
    @just --list

# ─── Quality ──────────────────────────────────────────────────────────

# Run all checks (lint + test + validate)
check: lint test validate

# Lint and format (pre-commit hooks)
lint:
    pixi run -- prek run --all-files --show-diff-on-failure --color=always

# Run test suite
test *args='':
    pixi run pytest tests/ -v {{ args }}

# Run only API search tests
test-api *args='':
    pixi run pytest tests/test_api_search.py -v {{ args }}

# Run only package search tests
test-pkg *args='':
    pixi run pytest tests/test_search.py -v {{ args }}

# Run structure tests
test-structure:
    pixi run pytest tests/test_structure.py -v

# Validate Typst code blocks in markdown docs
validate:
    pixi run python skills/typst/scripts/validate-examples.py

# Compile all .typ examples
compile-examples:
    #!/usr/bin/env bash
    set -euo pipefail
    for f in skills/typst/examples/*.typ; do
        typst compile "$f" /dev/null -f pdf && echo "OK: $f" || echo "FAIL: $f"
    done
    typst compile skills/typst/examples/package-example/lib.typ /dev/null -f pdf

# ─── Search ───────────────────────────────────────────────────────────

# Search Typst packages
search-pkg *args:
    pixi run python skills/typst/scripts/search-packages.py {{ args }}

# Search Typst API
search-api *args:
    pixi run python skills/typst/scripts/search-api.py {{ args }}

# ─── Data ─────────────────────────────────────────────────────────────

# Refresh package index from Typst Universe
fetch-packages:
    pixi run python tools/fetch-packages.py --output-dir skills/typst/data

# Refresh API index (requires typst-docs JSON)
fetch-api json_path:
    pixi run python tools/fetch-api-docs.py {{ json_path }} --out-dir skills/typst/data

# Build typst-docs and generate API index from source
fetch-api-from-source:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Cloning typst..."
    git clone --depth 1 https://github.com/typst/typst /tmp/typst-repo 2>&1 | tail -1
    echo "Building typst-docs..."
    cd /tmp/typst-repo && cargo build -p typst-docs --release 2>&1 | tail -1
    echo "Generating JSON..."
    mkdir -p /tmp/typst-docs-assets
    /tmp/typst-repo/target/release/typst-docs \
        --assets-dir /tmp/typst-docs-assets \
        --out-file /tmp/typst-api-raw.json
    echo "Building index..."
    pixi run python tools/fetch-api-docs.py /tmp/typst-api-raw.json --out-dir skills/typst/data
    rm -rf /tmp/typst-repo /tmp/typst-docs-assets /tmp/typst-api-raw.json

# ─── Dev ──────────────────────────────────────────────────────────────

# Show project stats
stats:
    #!/usr/bin/env bash
    echo "Docs:     $(find skills/typst -maxdepth 1 -name '*.md' | wc -l | xargs) files"
    echo "Examples: $(find skills/typst/examples -name '*.typ' | wc -l | xargs) files"
    echo "Scripts:  $(find skills/typst/scripts -name '*.py' | wc -l | xargs) files"
    echo "Tests:    $(pixi run pytest tests/ --co -q 2>/dev/null | tail -1)"
    echo "API:      $(pixi run python -c 'import json; d=json.load(open("skills/typst/data/api.json")); print(len(d), "entries")' 2>/dev/null)"
    echo "Packages: $(pixi run python -c 'import json; d=json.load(open("skills/typst/data/packages.json")); print(len(d), "packages")' 2>/dev/null)"
