# Development Guide

## What This Is

A skill that teaches AI agents how to work with Typst.
Everything agent-facing lives under `skills/typst/`. The root `README.md` is for humans browsing GitHub, and `skills/typst/` should not contain a separate human-facing `README.md`.

## Project Structure

```
repo root (NOT bundled)               skills/typst/ (bundled skill)
├── tools/          # Data generation  ├── SKILL.md       # Entry point
├── tests/          # Test suite       ├── *.md           # Reference docs
├── .github/        # CI workflows     ├── agents/        # Agent definitions
├── Justfile        # Task runner      ├── scripts/       # Search & validation
├── pixi.toml       # Dependencies    ├── data/          # JSON indexes
├── CLAUDE.md       # Dev guide        └── examples/      # Runnable .typ files
└── README.md       # Human readme
```

### Architecture: The Routing Rule

`SKILL.md` is the single entry point. It contains:

1. Detection patterns and quick reference
2. Two routing tables — **Writing Documents** (user-facing) and **Developing Packages and Templates** (developer-facing) — that direct agents to the right `*.md` file by task
3. Package search, common errors, and examples

**Every new `.md` file or capability MUST be registered in `SKILL.md`'s routing table.**
If it's not in the table, agents won't find it. Dead content is worse than no content.
This is enforced by `tests/test_structure.py`.

## Adding New Content

### New Reference Doc (e.g., `charts.md`)

1. Create `skills/typst/charts.md`
2. Start with a one-line cross-reference: `For language basics, see [basics.md](basics.md).`
3. Add an entry to the relevant routing table in `SKILL.md`
4. Keep `SKILL.md` as a router: add only the shortest task-oriented pointer, not a duplicate guide
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

- Python 3.10+ compatible (matches pixi.toml minimum)
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
just check   # runs lint + test + validate
```

Or individually:

```bash
just lint              # pre-commit hooks (ruff, format, etc.)
just test              # pytest (search, structure, API tests)
just validate          # inline Typst code blocks compile
just compile-examples  # all .typ examples compile
```

## Planned Capabilities

Track new features here. Move to the relevant `.md` once implemented.

- [x] **Package search**: BM25 index of Typst Universe packages, weekly CI refresh
- [x] **API reference search**: BM25 index with LaTeX symbol aliases, weekly CI refresh
- [x] **Tables and grids guide**: `tables.md`
- [x] **Academic writing guide**: `academic.md`
- [x] **CLI query guide**: `query.md` for `typst query`, metadata export, multi-pass
- [x] **Content introspection**: `advanced.md` section on `func()`, `fields()`, show rule decomposition
- [x] **Ecosystem tooling**: tinymist, typstyle, typst-package-check, tytanic in `package.md`
- [x] **Specialized agents**: `typst-verify`, `typst-package-qa`
- [ ] **Chart/visualization guide**: `charts.md` covering CetZ, plotst, and raw drawing
- [ ] **Slide/presentation guide**: `slides.md` for Polylux and touying
- [ ] **i18n guide**: CJK, RTL, multilingual document patterns

## Commit Style

Imperative mood, lowercase, no period. Prefix with scope when touching a single area.

```
charts: add CetZ line chart example
scripts: package search with embedded index
skill: register charts.md in routing table
```
