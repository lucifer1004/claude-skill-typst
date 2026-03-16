# Development Guide

## What This Is

A Claude Code / Cursor skill that teaches AI agents how to work with Typst.
Everything lives under `skills/typst/`. The root `README.md` is for humans browsing GitHub.

## Project Structure

```
repo root (NOT bundled)               skills/typst/ (bundled skill)
├── tools/                            ├── SKILL.md           # Entry point
│   └── fetch-packages.py            ├── *.md               # Reference docs
├── .github/workflows/                ├── scripts/
│   └── update-packages.yml          │   └── search-packages.py
├── CLAUDE.md                         ├── data/
└── README.md                         │   ├── packages.json
                                      │   └── packages-bm25.json
                                      └── examples/
                                          └── package-example/
```

### Architecture: The Routing Rule

`SKILL.md` is the single entry point. It contains:

1. Detection patterns and quick reference
2. Two routing tables — **Writing Documents** (user-facing) and **Developing Packages and Templates** (developer-facing) — that direct agents to the right `*.md` file by task
3. Package search, common errors, and examples

**Every new `.md` file or capability MUST be registered in `SKILL.md`'s routing table.**
If it's not in the table, agents won't find it. Dead content is worse than no content.

## Adding New Content

### New Reference Doc (e.g., `charts.md`)

1. Create `skills/typst/charts.md`
2. Start with a one-line cross-reference: `For language basics, see [basics.md](basics.md).`
3. Add an entry to the "Quick Reference" table in `SKILL.md`
4. Add a "When to Use" subsection in `SKILL.md` (2-4 bullet points)
5. If the doc references runnable examples, put them in `examples/`

### New Script (e.g., `scripts/search-packages.py`)

1. Place under `skills/typst/scripts/` (not `examples/` — scripts are tools, examples are demos)
2. Must be self-contained: stdlib-only or with clear dep instructions
3. Must have `--help` with usage examples
4. Must work without network access where possible (prefer embedded data over API calls)
5. Reference the script from the relevant `.md` doc AND from `SKILL.md`

### New Embedded Data (e.g., `data/packages.json`)

1. Place under `skills/typst/data/`
2. Include a generation script under `tools/` at the repo root (NOT in the bundle)
3. Document the data schema in the generation script
4. Keep file sizes reasonable — agents load these into context
5. Add a CI workflow in `.github/workflows/` to refresh the data on a cron schedule

## Writing Standards

### For `.md` Reference Docs

- **Lead with the pattern, not the explanation.** Show the code first, explain after.
- **No prose walls.** Tables, code blocks, and bullet points. Agents parse structure, not paragraphs.
- **Cross-reference siblings.** Every doc should link to related docs in its first line.
- **Typst code blocks use ```` ```typst ```` fencing.** Shell commands use ```` ```bash ````.
- **Every code example must compile.** If it's a snippet that needs context, say so explicitly.

### For Scripts

- Python 3.8+ compatible (oldest version still common in the wild)
- `argparse` for CLI, with `--help` that shows real usage
- Print structured output (tables or `--json`) so agents can parse results
- Exit code 0 on success, non-zero on failure

### For Examples

- Each `.typ` example must compile standalone: `typst compile examples/foo.typ`
- If it needs `--root`, document that in a comment at the top of the file
- Keep examples focused — one concept per file, not a kitchen sink

## Validation

Before committing, verify:

```bash
# All .typ examples compile
for f in skills/typst/examples/*.typ; do
  typst compile "$f" /dev/null && echo "OK: $f" || echo "FAIL: $f"
done

# Package example compiles
typst compile skills/typst/examples/package-example/lib.typ /dev/null

# Python scripts have valid syntax
python3 -m py_compile skills/typst/examples/perf-timings.py
python3 -m py_compile skills/typst/scripts/search-packages.py

# Package search works
python3 skills/typst/scripts/search-packages.py "chart" --top 3
```

## Planned Capabilities

Track new features here. Move to the relevant `.md` once implemented.

- [x] **Package search**: BM25 index of 1,188 Typst Universe packages (`scripts/search-packages.py`), weekly CI refresh
- [ ] **Chart/visualization guide**: `charts.md` covering CetZ, plotst, and raw drawing
- [ ] **Slide/presentation guide**: `slides.md` for Polylux and touying
- [ ] **Academic writing guide**: `academic.md` for papers, theses, citations
- [ ] **i18n guide**: CJK, RTL, multilingual document patterns

## Commit Style

Imperative mood, lowercase, no period. Prefix with scope when touching a single area.

```
charts: add CetZ line chart example
scripts: package search with embedded index
skill: register charts.md in routing table
```
