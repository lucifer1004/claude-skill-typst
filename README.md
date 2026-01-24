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

| File            | Description                                  |
| --------------- | -------------------------------------------- |
| `SKILL.md`      | Main entry point with quick reference        |
| `basics.md`     | Language fundamentals, types, imports, paths |
| `advanced.md`   | State, context, query, XML parsing           |
| `template.md`   | Template development, set/show rules         |
| `package.md`    | Package development and publishing           |
| `conversion.md` | Markdown/LaTeX to Typst conversion           |
| `debug.md`      | Debugging techniques for agents              |
| `perf.md`       | Performance profiling and timings            |
| `examples/`     | Runnable examples (including perf test)      |

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
