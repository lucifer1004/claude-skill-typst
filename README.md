# Typst Skill for Claude Code

A comprehensive skill for Typst document creation and package development. The
current main branch targets Typst 0.15 by default, with a Typst 0.14.2
compatibility path for legacy users.

## Installation

One-line install:

```bash
npx skills add https://github.com/lucifer1004/claude-skill-typst
```

Manual install:

```bash
git clone https://github.com/lucifer1004/claude-skill-typst.git ~/.claude/skills/typst
```

## Quick Start

```bash
# Compile a minimal document
cat > /tmp/hello.typ <<'EOF'
#set page(paper: "a4", margin: 2cm)
= Hello Typst

This is a minimal document.
EOF

typst compile /tmp/hello.typ
```

Verify output (HTML export for agents, PNG for visual checks):

```bash
typst compile /tmp/hello.typ /dev/stdout -f html --features html 2>/dev/null
typst compile /tmp/hello.typ "page-{p}.png" -f png
```

## Contents

| File            | Audience   | Description                                             |
| --------------- | ---------- | ------------------------------------------------------- |
| `SKILL.md`      | Both       | Main entry point with quick reference                   |
| `basics.md`     | Both       | Language fundamentals, imports, functions               |
| `types.md`      | Both       | Data types, operators, string/array/dict/color/datetime |
| `styling.md`    | Users      | Set/show rules, page layout, images, fonts, figures     |
| `tables.md`     | Users      | Tables, grids, cell spans, borders, data tables         |
| `academic.md`   | Users      | Papers, bibliography, theorems, equations               |
| `conversion.md` | Users      | Markdown/LaTeX to Typst conversion                      |
| `cli.md`        | Both       | Typst CLI commands, export options, fonts, packages     |
| `query.md`      | Both       | CLI introspection, metadata export, multi-pass builds   |
| `advanced.md`   | Developers | State, context, query, content introspection, XML       |
| `template.md`   | Developers | Reusable template function patterns                     |
| `package.md`    | Developers | Package development, testing, and publishing            |
| `debug.md`      | Developers | Verification methods (HTML/PNG/pdftotext)               |
| `perf.md`       | Developers | Performance profiling and timings                       |
| `examples/`     | Both       | Runnable examples                                       |
| `agents/`       | Agents     | Specialized agents (typst-verify, typst-package-qa)     |

## Search Tools

```bash
# Search Typst packages
just search-pkg "chart visualization"

# Search Typst API (functions, methods, types, symbols)
just search-api "image width fit"
just search-api "rightarrow" --kind symbol   # LaTeX names work
just search-api --name str.position -v       # Exact lookup
just search-api "asset"                      # Typst 0.15 default API
just search-api "path" --channel 0.14.2      # Typst 0.14 compatibility
```

## Development

```bash
just              # List all recipes
just check        # Run lint + test + validate
just test         # Run test suite
just validate     # Validate inline Typst code blocks in docs
just stats        # Show project stats
```

## Usage

Once installed, Claude Code will automatically activate this skill when:

- Working with `.typ` files
- User mentions "typst" or related terms
- Creating or modifying Typst documents

## Requirements

- [Typst CLI](https://typst.app) 0.15+ recommended
- [just](https://just.systems) (optional, for development)
- [pixi](https://pixi.sh) (optional, for development)

For users who are still on Typst 0.14.2, use the `typst-0.14.2` repository tag
for the previous skill snapshot or the `--channel 0.14.2` API search option on
main.

## License

MIT
