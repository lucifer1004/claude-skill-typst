# Typst CLI

For full option lists, run `typst <command> --help`. This page is a routing index plus a few CLI gotchas that are not already covered elsewhere.

## What This Adds

- Pointers to the right existing reference doc.
- CI/export flag combinations that do not fit a language or debugging guide.
- Pitfalls around PDF standards, dependency files, package caches, templates, and page-numbered outputs.

## Command Choice

| Task                                                                                              | Use                      |
| ------------------------------------------------------------------------------------------------- | ------------------------ |
| Validate or inspect rendered output                                                               | [debug.md](debug.md)     |
| Use `typst query`, `--field`, `--one`, `--target html`, or multi-pass builds                      | [query.md](query.md)     |
| Fix project-root or `/absolute/path` import issues                                                | [basics.md](basics.md)   |
| Configure fonts or use `typst fonts` / `--font-path`                                              | [styling.md](styling.md) |
| Profile with `--timings`                                                                          | [perf.md](perf.md)       |
| Develop or publish packages                                                                       | [package.md](package.md) |
| Initialize from a template, produce PDF/A or PDF/UA, emit dependency files, or pin package caches | This page                |

## CI Export Recipe

```bash
typst compile doc.typ out.pdf --root . \
  --creation-timestamp "$SOURCE_DATE_EPOCH" \
  --package-cache-path ./.typst-cache \
  --deps deps.json --deps-format json
```

Use this shape when comparing artifacts across machines. Pin the root, timestamp, and package cache; record dependencies for rebuild logic. `--deps-format make` is for Makefiles; `zero` handles paths that cannot be represented as Unicode.

## PDF Standards

```bash
typst compile doc.typ out.pdf --pdf-standard a-4
typst compile doc.typ out.pdf --pdf-standard ua-1
typst compile doc.typ out.pdf --pdf-standard a-4,ua-1
```

Use CLI values like `1.7`, `2.0`, `a-4`, or `ua-1`; do not write `pdf/a-4` or `pdf/ua-1`. Typst 0.14 writes tagged PDFs by default. `--no-pdf-tags` is an explicit size/compatibility tradeoff.

## Template Init

```bash
typst init @preview/charged-ieee
typst init @preview/charged-ieee:0.1.0 my-paper
typst init @local/my-template:0.1.0 draft --package-path ./packages
```

Use `@local/...` with `--package-path` when testing templates before publication.

## Gotchas

- `-` means stdin for input and stdout for output, but writing PDF/PNG bytes to a terminal is rarely useful.
- Multi-page PNG/SVG outputs need a template such as `page-{p}.png`; `{0p}` pads page numbers and `{t}` inserts total page count.
- `--pages` uses one-indexed physical page numbers, not the document's printed page counter.
- `watch` is for human feedback loops; use `compile` or `query` in CI.
- `typst completions <shell>` exists for shell setup, but agents normally do not need it.

## When to Read Help

Use `typst compile --help`, `typst watch --help`, `typst query --help`, or `typst init --help` when you need the complete current option list. This page is intentionally not a mirror of those outputs.
