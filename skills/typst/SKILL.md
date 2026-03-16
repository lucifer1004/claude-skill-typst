---
name: typst
description: 'Typst document creation and package development. Use when: (1) Working with .typ files, (2) User mentions typst, typst.toml, or typst-cli, (3) Creating or using Typst packages, (4) Developing document templates, (5) Converting Markdown/LaTeX to Typst'
---

# Typst

Modern typesetting system — simpler than LaTeX, faster compilation, programmable.

## Compilation

```bash
typst compile document.typ              # compile once
typst compile document.typ output.pdf   # explicit output path
typst compile src/main.typ --root .     # set project root for /path imports
typst watch document.typ                # recompile on change
```

Agents cannot preview PDFs. Verify via exit code and `pdftotext`:

```bash
typst compile document.typ && pdftotext document.pdf - | head -20
```

## Minimal Document

```typst
#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt)

= Title

Content goes here.
```

## Writing Documents

| When you need to...                           | Read                           |
| --------------------------------------------- | ------------------------------ |
| Learn syntax, types, imports, path resolution | [basics.md](basics.md)         |
| Style pages, headings, figures, layout        | [styling.md](styling.md)       |
| Convert from Markdown or LaTeX                | [conversion.md](conversion.md) |

**Start with [basics.md](basics.md)** — it covers modes, imports, data types, functions, and common pitfalls.

## Developing Packages and Templates

| When you need to...                       | Read                       |
| ----------------------------------------- | -------------------------- |
| Use state, context, query, or parse XML   | [advanced.md](advanced.md) |
| Create a reusable template function       | [template.md](template.md) |
| Create or publish a package               | [package.md](package.md)   |
| Debug output (pdftotext, repr, measure)   | [debug.md](debug.md)       |
| Profile performance (--timings, hotspots) | [perf.md](perf.md)         |

[basics.md](basics.md) is also the foundation for developers.

## Finding Packages

Search the embedded index of 1,188 Typst Universe packages (updated weekly):

```bash
python3 scripts/search-packages.py "what you need"
python3 scripts/search-packages.py "chart" --category visualization
python3 scripts/search-packages.py --category cv --top 5
python3 scripts/search-packages.py --list-categories
```

### Import Pattern

```typst
#import "@preview/package-name:version": *
#import "@preview/package-name:version": specific-func
```

## Common Errors

| Error                                  | Cause                | Fix                                       |
| -------------------------------------- | -------------------- | ----------------------------------------- |
| "unknown variable"                     | Undefined identifier | Check spelling, ensure `#let` before use  |
| "expected X, found Y"                  | Type mismatch        | Check function signature in docs          |
| "file not found"                       | Bad import path      | Paths resolve relative to current file    |
| "unknown font"                         | Font not installed   | Use system fonts or web-safe alternatives |
| "maximum function call depth exceeded" | Deep recursion       | Use iteration instead                     |

## Examples

| Example                                             | Description                                          |
| --------------------------------------------------- | ---------------------------------------------------- |
| [basic-document.typ](examples/basic-document.typ)   | Complete beginner document with all common elements  |
| [template-report.typ](examples/template-report.typ) | Reusable template with headers, counters, note boxes |
| [package-example/](examples/package-example/)       | Minimal publishable package with submodules          |

## Dependencies

- **typst CLI**: Install from https://typst.app or via package manager
  - macOS: `brew install typst`
  - Linux: `cargo install typst-cli`
  - Windows: `winget install typst`
- **pdftotext** (optional): For text-level output verification
- **Python 3.8+** (optional): For package search script
