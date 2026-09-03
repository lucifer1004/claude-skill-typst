# Migrating to Typst 0.15

For converting from LaTeX/Markdown, see [conversion.md](conversion.md). For symbol and rendering traps, see [debug.md](debug.md).

Typst 0.15 removed long-deprecated APIs. If your Typst knowledge predates 0.15, check this page first: outdated patterns either fail loudly (removed functions) or shift silently (layout changes).

## Removed in 0.15 (compile errors)

| Old (≤ 0.14) | New (0.15+) |
| --- | --- |
| `path(...)` drawing element | `curve(...)` |
| `pattern` type | `tiling` |
| `pdf.embed(...)` | `pdf.attach(...)` |
| `json.decode(bytes)` and siblings (`cbor/csv/toml/xml/yaml.decode`, `image.decode`) | pass `bytes` to the top-level function: `json(bytes)` |
| `typst query doc.typ "<sel>"` (CLI) | `typst eval --in doc.typ 'query(<sel>)'` — see [query.md](query.md) |
| Backslashes in paths (`"chapters\intro.typ"`) | forward slashes only, on all platforms |

## Silent behavior changes

| Area | Change |
| --- | --- |
| Baselines | Boxes, blocks, list items, and equations now retain baseline info — an inline `box(inset: ..)` aligns with surrounding text. Old manual alignment tweaks may now misalign. |
| Math `class` | Applies to its direct body only, not recursively |
| Math delimiters | More symbols (e.g. `chevron.l`) are callable and produce `lr(...)`; `chevron.l(x)` now renders ⟨x⟩ instead of literal parentheses |
| Math glyph stretch | `lr`/`stretch` size ratios resolve against the base glyph size; display-style glyphs (integrals) may need larger explicit sizes |
| Calligraphic style | New Computer Modern 8.1 changed `cal()` letterforms; restore the old look with `#show math.equation: set text(stylistic-set: 6)` |
| HTML export | `box`/`block` and paragraph grouping reworked (fewer stray `<p>`); `html.script`/`html.style` accept strings only; output minified by default (`--pretty` to opt out) |
| Variable fonts | Family suffixes "Variable"/"Var"/"VF" are trimmed — select the plain family name and control axes via `weight`/`stretch`/`variations` |
| Stricter validation | `array.slice`, the `str` constructor, and `text.features` now reject invalid input that was previously tolerated |

Renamed citation styles and symbols, and zero in numbering systems that can't express it, only produce compiler warnings for now — they become hard errors later.

## New in 0.15 (usable now)

- `within` selector: `query(heading.within(<appendix>))` — scoped introspection without location bookkeeping
- `path` type: real file-system paths, passable across package boundaries
- `divider` element: a thematic break that templates can style
- Multiple `bibliography(...)` calls in one document
- HTML export: equations become MathML automatically (no `html.frame` SVG workaround needed)
- Bundle export (experimental): one project → multiple output files
- `list.marker-align` (its new default changes list marker alignment vs 0.14)
- Spot colors, multiple PDF standards in one run, weak + fractional spacing

Verify anything version-sensitive against the API index before using it:

```bash
python3 scripts/search-api.py --name curve
```
