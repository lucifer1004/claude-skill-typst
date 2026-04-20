---
name: typst
description: 'Typst document creation and package development. Use when: (1) Working with .typ files, (2) User mentions typst, typst.toml, or typst-cli, (3) Creating or using Typst packages, (4) Developing document templates, (5) Converting Markdown/LaTeX to Typst'
---

# Typst

## Compilation

```bash
typst compile document.typ              # compile once → PDF
typst compile document.typ output.pdf   # explicit output path
typst compile document.typ -f png       # export as PNG image
typst compile src/main.typ --root .     # set project root for /path imports
typst watch document.typ                # recompile on change
typst query document.typ "<label>"      # extract metadata as JSON (see query.md)
```

Agent verification — choose by what you need to check (see [debug.md](debug.md) for details):

| Method      | Command                                                                 | Best for                                  |
| ----------- | ----------------------------------------------------------------------- | ----------------------------------------- |
| HTML export | `typst compile doc.typ /dev/stdout -f html --features html 2>/dev/null` | Text content, structure, headings, tables |
| PNG export  | `typst compile doc.typ page-{p}.png -f png`                             | Visual layout, alignment, spacing, fonts  |
| pdftotext   | `typst compile doc.typ && pdftotext doc.pdf -`                          | Fallback for page-specific content        |

## Minimal Document

```typst
#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt)

= Title

Content goes here.
```

## Writing Documents

**Starting a new document?** Copy the closest recipe from [Examples](#examples) below — it's faster than starting blank and each row names the docs to read next.

| When you need to...                                | Read                           |
| -------------------------------------------------- | ------------------------------ |
| Learn syntax, imports, functions, control flow     | [basics.md](basics.md)         |
| Learn data types, operators, string/array methods  | [types.md](types.md)           |
| Style pages, headings, figures, layout             | [styling.md](styling.md)       |
| Tables, grids, cell spans, borders, data tables    | [tables.md](tables.md)         |
| Academic papers, bibliography, theorems, equations | [academic.md](academic.md)     |
| Convert from Markdown or LaTeX                     | [conversion.md](conversion.md) |
| Extract data from documents, multi-pass builds     | [query.md](query.md)           |

## Developing Packages and Templates

| When you need to...                         | Read                       |
| ------------------------------------------- | -------------------------- |
| State, counters, in-document `query()`, XML | [advanced.md](advanced.md) |
| CLI query, metadata export, multi-pass      | [query.md](query.md)       |
| Create a reusable template function         | [template.md](template.md) |
| Create or publish a package                 | [package.md](package.md)   |
| Verify output (HTML/PNG/pdftotext, repr)    | [debug.md](debug.md)       |
| Profile performance (--timings, hotspots)   | [perf.md](perf.md)         |

[basics.md](basics.md) and [types.md](types.md) are also the foundation for developers.

## Finding Packages

Search the embedded index of Typst Universe packages (updated weekly):

```bash
python3 scripts/search-packages.py "what you need"
python3 scripts/search-packages.py "chart" --category visualization
python3 scripts/search-packages.py --category cv --top 5
python3 scripts/search-packages.py --list-categories
```

## Common Errors

| Error                                            | Cause                        | Fix                                                  |
| ------------------------------------------------ | ---------------------------- | ---------------------------------------------------- |
| "unknown variable"                               | Undefined identifier         | Check spelling, ensure `#let` before use             |
| "expected X, found Y"                            | Type mismatch                | Check function signature in docs                     |
| "file not found"                                 | Bad import path              | Paths resolve relative to current file               |
| "unknown font"                                   | Font not installed           | Use system fonts or web-safe alternatives            |
| "maximum function call depth exceeded"           | Deep recursion               | Use iteration instead                                |
| "can only be used when context is known"         | Missing `context` wrapper    | Wrap in `context { ... }`                            |
| "unexpected argument"                            | `=` instead of `:` for args  | Named args use `:` syntax: `func(name: value)`       |
| "variables from outside are read-only"           | Mutating captured variable   | Use loop accumulation or `state()` — see advanced.md |
| "expected content, found string" (or vice versa) | Content/string type mismatch | Use `[#str-var]` to embed string in content          |
| set/show rule has no effect                      | Rule placed after content    | Place set/show rules before the content they target  |

## Examples

Copy the closest starter, adjust, compile. For CVs, letters, or slides, search packages: `python3 scripts/search-packages.py --category cv` (or `letter`, `presentation`).

| Example                                             | Start here when you want...              | Next read                                        |
| --------------------------------------------------- | ---------------------------------------- | ------------------------------------------------ |
| [basic-document.typ](examples/basic-document.typ)   | A short note or memo                     | [basics.md](basics.md), [styling.md](styling.md) |
| [styled-document.typ](examples/styled-document.typ) | A multi-section report with page styling | [styling.md](styling.md), [tables.md](tables.md) |
| [template-report.typ](examples/template-report.typ) | A reusable template for a series         | [template.md](template.md)                       |
| [tables-showcase.typ](examples/tables-showcase.typ) | A data-heavy doc (tables, CSV/JSON)      | [tables.md](tables.md), [types.md](types.md)     |
| [academic-paper.typ](examples/academic-paper.typ)   | A paper with citations, theorems, math   | [academic.md](academic.md)                       |
| [query-export.typ](examples/query-export.typ)       | Metadata export or multi-pass builds     | [query.md](query.md)                             |
| [package-example/](examples/package-example/)       | A publishable package                    | [package.md](package.md)                         |

## Dependencies

- **typst CLI**: Install from https://typst.app or via package manager
  - macOS: `brew install typst`
  - Linux: `cargo install typst-cli`
  - Windows: `winget install typst`
- **pdftotext** (optional): For text-level output verification
- **Python 3.10+** (optional): For package search and validation scripts
- **jq** (optional): For parsing JSON output from `typst query` in shell scripts

## API Reference Search

Search the embedded index of Typst API functions, methods, and constructors:

```bash
python3 scripts/search-api.py "image width fit"
python3 scripts/search-api.py "color lighten" --kind method
python3 scripts/search-api.py --name str.position -v
python3 scripts/search-api.py "rightarrow" --kind symbol   # LaTeX names work
python3 scripts/search-api.py --list-categories
```

## Ecosystem Tools

Ecosystem tools: **tinymist** (LSP/editor), **typstyle** (formatter), **typst-package-check** (package validator), **tytanic** (visual test runner). For package tooling details, see [package.md](package.md).
