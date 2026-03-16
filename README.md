# Typst Skill for Claude Code

A comprehensive skill for Typst document creation and package development.

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

Verify output text (optional):

```bash
pdftotext /tmp/hello.pdf - | head -20
```

## Contents

| File            | Audience   | Description                                      |
| --------------- | ---------- | ------------------------------------------------ |
| `SKILL.md`      | Both       | Main entry point with quick reference            |
| `basics.md`     | Both       | Language fundamentals, imports, functions        |
| `types.md`      | Both       | Data types, operators, string/array/dict methods |
| `styling.md`    | Users      | Set/show rules, page layout, figures, labels     |
| `tables.md`     | Users      | Tables, grids, cell spans, borders, data tables  |
| `academic.md`   | Users      | Papers, bibliography, theorems, equations        |
| `conversion.md` | Users      | Markdown/LaTeX to Typst conversion               |
| `advanced.md`   | Developers | State, context, query, counters, XML parsing     |
| `template.md`   | Developers | Reusable template function patterns              |
| `package.md`    | Developers | Package development and publishing               |
| `debug.md`      | Developers | Debugging techniques for agents                  |
| `perf.md`       | Developers | Performance profiling and timings                |
| `examples/`     | Both       | Runnable examples (including perf test)          |

## Usage

Once installed, Claude Code will automatically activate this skill when:

- Working with `.typ` files
- User mentions "typst" or related terms
- Creating or modifying Typst documents

## Examples

```bash
# Compile included examples
typst compile ~/.claude/skills/typst/examples/basic-document.typ
typst compile ~/.claude/skills/typst/examples/template-report.typ
typst compile ~/.claude/skills/typst/examples/package-example/lib.typ
```

## Requirements

- [Typst CLI](https://typst.app) installed
- `pdftotext` (optional, for debugging)

## License

MIT
