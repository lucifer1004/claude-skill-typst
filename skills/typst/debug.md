# Typst Debugging Techniques

For language basics, see [basics.md](basics.md). For type inspection (`type()`, `repr()`), see [types.md](types.md). For state/context debugging, see [advanced.md](advanced.md).

## Common Errors & Symbol Gotchas (0.15)

Recurring failures hit when authoring math-heavy documents. Each cost a compile cycle; listed with the exact error and the fix.

### Math symbols that don't exist under the name you'd guess

| You wrote                                   | Error                     | Correct                                                                        |
| ------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------ |
| `angle.l` / `angle.r` (for ⟨ ⟩)             | `unknown symbol modifier` | `chevron.l` / `chevron.r` (or literal `⟨ ⟩` inside `lr(...)`)                  |
| `check(x)` (háček accent)                   | `unknown variable: check` | `caron(x)` — the check/háček accent is named `caron`                           |
| `times.circle` / `times.circle.big` (for ⊗) | `unknown symbol modifier` | literal `⊗` glyph in the source. **Not** `product.co` (that's the coproduct ∐) |

General rule: when a `symbol.modifier` chain errors with *"unknown symbol modifier"*, the modifier path is wrong — verify against the API data (`scripts/search-api.py`) or just paste the literal Unicode glyph into the math, which always works. Math accent functions are `hat, tilde, macron/overline, dot, dot.double, acute, grave, breve, circle, caron, arrow` — there is **no** `check`, `bar` is `macron`, etc.

### Sub/superscript swallows the following function-argument group

**The single most common silent math error.** A script whose base is an **identifier or string** — a letter (`_c`, `_n`), a spelled-out Greek name, or a quoted word (`_"loc"`, `^"glob"`) — does not "close": Typst parses the following `c(N)` or `"loc"[x]` as a **function call / index** and folds it *into* the script. Affects both `_` and `^`, both `(...)` and `[...]`. It compiles fine; only PNG inspection reveals it.

```typst
$ alpha_c(N) $                    // WRONG -> alpha_{c(N)}   (letter subscript: c(N) parsed as a call!)
$ nu_n(hat(h)) $                  // WRONG -> nu_{n(hat h)}
$ alpha_c^"glob"(kappa) $         // WRONG -> alpha_c^{glob(kappa)}   (kappa in the superscript!)
$ cal(S)_"loc"[nu_n; kappa] $     // WRONG -> S_{loc[nu_n;kappa]}     (bracket in the subscript!)
```

Two equivalent fixes (both render the argument at baseline with correct function-application spacing — no visible gap):

```typst
$ alpha_c^"glob" (kappa) $        // (a) a SPACE after the script  <- simplest, matches common house style
$ alpha_c^("glob")(kappa) $       // (b) parenthesize the script BASE, closing it
```

Note: only a **digit** subscript is safe — `F_2(kappa)`, `L_2(x)` — because a number isn't callable; that is why `F_2(kappa)` renders fine but `alpha_c(N)` does not. A following superscript also closes a subscript, so `A_alpha^((n))[...]` is fine; and when the call-glyph *is* the intended subscript (`nabla_frak(M)` → ∇\_𝔐) the folding is what you want. Otherwise always put a space (or parens) before an argument that follows a letter or string script. Grep for the bug: `grep -noE '(\^|_)("[^"]*"|[A-Za-z]+)[([]' file.typ`.

**False alarms — leave these alone.** A script whose base is *already a parenthesised group* is closed, so a following `(…)`/`[…]` stays at baseline and does **not** swallow. Verified by PNG-stacking the pairs: `bb(E)_(nu_n)[v v^top]` and `Phi^(-1)(x)` render *identically* with or without an inserted space. So the two commonest-looking "offenders" are not bugs and must not be "fixed": expectation brackets `bb(E)_(nu_n)[…]` and inverse-function args `Phi^(-1)(x)`. The grep above already excludes paren-group scripts (`_(...)`); reach for the space/paren fix only when the base is a bare letter or a `"quoted"` word (e.g. `delta r_"op"(a)` → `delta r_"op" (a)`).

**Same root cause — the fraction `/`.** `A(x) / B(y)` binds the slash to the single adjacent atom: numerator `(x)`, denominator `B`, stranding `A` and `(y)` into a product. `cal(Z)(tilde(S)) / cal(Z)(0)` renders as `𝒵·(S̃/𝒵)·(0)`, not `𝒵(S̃)/𝒵(0)`. Use `frac(cal(Z)(tilde(S)), cal(Z)(0))` (or parenthesise each side) whenever a numerator/denominator is a product or function application; bare `a/b` is only safe for single atoms (`1/2`, `D/2`, `(…)/2`). Grep for a function application sitting next to a bare slash: `grep -noE '\)[^)]*\) / ' file.typ`.

### Math-mode `"--"` is NOT converted to an en-dash

The markup-mode smartquote pass (`--` → –, `---` → —) does **not** run inside `$...$`. `1.60 "--" 1.61` renders as two literal hyphens.

```typst
$ 1.60 "--" 1.61 $     // WRONG: prints 1.60 -- 1.61
$ 1.60"–"1.61 $        // RIGHT: literal en-dash, or use `dash.en`
```

### Wide display equation collides with its `(N)` number

Two equations joined by `quad`/`space` on one display line overflow into the equation number. Break with `\` into stacked lines (the number then centers on the block):

```typst
$
  A = product_a Z(S^a), \        // was: ..., quad Z(S^a) = integral ...  (ran into "(20)")
  Z(S^a) = integral ... .
$
```

### Image path "would escape the project root"

`image("../plots/x.png")` fails with *"path ... would escape the project root"* when the file sits below the image. The sandbox root defaults to the `.typ` file's directory. Set `--root` to a common ancestor:

```bash
# file: notes/doc.typ, image: plots/x.png  -> root must contain both
typst compile --root . notes/doc.typ          # run from repo root
```

Relative image paths resolve against the `.typ` file but must stay inside `--root`.

### BibTeX LaTeX accents the Hayagriva parser can't read

`bibliography("refs.bib")` handles most LaTeX accents (`{\"u}`→ü, `{\H{o}}`→ő, `{\v{c}}`→č, ``  {\`e} ``→è) but chokes on the dotless-i combo, rendering a literal backslash:

```bibtex
author = {Ma{\"\i}da}   % WRONG: renders as "Ma\ida"
author = {Maïda}        % RIGHT: paste the Unicode character
```

When a name renders with a stray backslash, this is why.

### Fast way to settle a rendering question

When unsure which of several markup variants renders correctly (e.g. the subscript-bracket case above), compile a throwaway `.typ` with all candidates stacked and PNG-inspect — one render decides it instead of guessing in the main document:

```bash
printf 'A: $cal(S)_"loc"[x]$\nB: $cal(S)_("loc")[x]$\n' > /tmp/t.typ
typst compile --root / /tmp/t.typ /tmp/t.png --ppi 150 && echo done   # then read /tmp/t.png
```

## Agent Verification Methods

Agents cannot preview PDFs directly. Three methods, choose by what you need to check:

### HTML Export — Text and Structure

Outputs semantic HTML (headings → `<h2>`, tables → `<table>`, figures → `<figure>`). Best for verifying content, structure, and data correctness.

```bash
typst compile document.typ /dev/stdout -f html --features html 2>/dev/null
typst compile document.typ /dev/stdout -f html --features html 2>/dev/null | grep -i "expected text"
```

HTML export is experimental and ignores page-specific features (headers, footers, page numbers).

### PNG Export — Visual Layout

Exports rendered pages as images. Use when layout matters — alignment, spacing, font rendering, page breaks, multi-column, headers/footers. Requires a multimodal agent.

```bash
# Export all pages ({p} = page number, required for multi-page documents)
typst compile document.typ "page-{p}.png" -f png

# Export specific pages only
typst compile document.typ "page-{p}.png" -f png --pages 1-3

# Higher resolution (default: 144 PPI)
typst compile document.typ "page-{p}.png" -f png --ppi 288
```

Then read the PNG file(s) to visually inspect the rendered output.

### pdftotext — Fallback

Plain text extraction. Use when HTML export fails or for quick page-count checks.

```bash
typst compile document.typ && pdftotext document.pdf -
```

## Object Inspection with repr

Use `repr()` to inspect complex objects during development:

```typst
// Basic inspection
#repr(some-variable)

// Inspect function arguments
#let my-func(..args) = {
  [DEBUG: #repr(args.pos()) | #repr(args.named())]
  // actual logic...
}

// Inspect content structure
#let c = [Hello *world*]
#repr(c)  // Shows internal content structure

// Inspect dictionary/array
#let data = (name: "test", items: (1, 2, 3))
#repr(data)  // "(name: "test", items: (1, 2, 3))"
```

### Type + Repr Pattern

```typst
// Full debug info
#let debug-value(v) = {
  text(fill: red, size: 8pt)[
    [#type(v)] #repr(v)
  ]
}

#debug-value((a: 1, b: (2, 3)))
// Output: [dictionary] (a: 1, b: (2, 3))
```

### Conditional Debug Output

```typst
#let DEBUG = true

#let debug(label, value) = if DEBUG {
  block(
    fill: yellow.lighten(80%),
    inset: 4pt,
    radius: 2pt,
    text(size: 8pt, fill: red)[#label: #repr(value)]
  )
}

// Usage
#debug("config", config)
#debug("items count", items.len())
```

## Layout Debugging with measure

Use `measure()` to debug sizing and spacing issues. Requires `context`.

### Basic Measurement

```typst
#context {
  let size = measure([Hello World])
  [Width: #size.width, Height: #size.height]
}
// Output: Width: 52.5pt, Height: 10pt
```

### Measure + Repr + Place Pattern

For debugging layout issues, combine measurement with visual markers:

```typst
// Debug helper: shows measurement overlay
#let debug-measure(content, label: none) = context {
  let size = measure(content)
  let lbl = if label != none { label } else { "" }

  box[
    #content
    #place(
      top + left,
      dx: size.width,
      text(size: 6pt, fill: red)[
        #lbl #repr(size.width) × #repr(size.height)
      ]
    )
  ]
}

// Usage
#debug-measure([Some content], label: "box1")
```

### Visual Boundary Boxes

```typst
// Show element boundaries
#let debug-box(content) = context {
  let size = measure(content)
  box(
    stroke: 0.5pt + red,
    inset: 0pt,
  )[
    #content
    #place(
      bottom + right,
      text(size: 5pt, fill: red)[#repr(size)]
    )
  ]
}

#debug-box[This text has visible boundaries]
```

### Spacing Debug

```typst
// Visualize spacing between elements
#let debug-spacing(a, b, gap: 1em) = context {
  let size-a = measure(a)
  let size-b = measure(b)

  box[
    #a
    #h(gap)
    #place(
      dx: size-a.width,
      text(size: 6pt, fill: blue)[← #repr(gap) →]
    )
    #b
  ]
}

#debug-spacing([Left], [Right], gap: 2em)
```

### Page Position Debug

```typst
// Show current position on page
#let debug-position() = context {
  let pos = here().position()
  place(
    dx: -20pt,
    text(size: 5pt, fill: gray)[
      (#repr(pos.x), #repr(pos.y))
    ]
  )
}

Some content #debug-position()
More content #debug-position()
```

## State Debugging

```typst
#let my-state = state("debug-example", 0)

// Track state changes
#let debug-state-change(label) = context {
  let val = my-state.get()
  text(size: 7pt, fill: purple)[
    [#label] state = #repr(val)
  ]
}

#debug-state-change("before")
#my-state.update(n => n + 1)
#debug-state-change("after")
```

## Query Debugging

```typst
// Debug query results
#context {
  let headings = query(heading)

  block(
    fill: luma(240),
    inset: 8pt,
    width: 100%,
  )[
    *Query Debug: #headings.len() headings found*
    #for (i, h) in headings.enumerate() {
      [

        #(i + 1). Level #h.level: #repr(h.body)
      ]
    }
  ]
}
```

## Assertion-Based Debugging

```typst
// Fail fast with clear messages
#let validate-config(cfg) = {
  assert(type(cfg) == dictionary, message: "Config must be dictionary")
  assert("name" in cfg, message: "Config missing required 'name' field")
  assert(cfg.at("size", default: 10) > 0, message: "Size must be positive")
}

#validate-config((name: "test", size: 12))
```

## Production Cleanup

Remove debug code before publishing:

```typst
// Single flag controls all debug output
#let DEBUG = false  // Set to true during development

#let debug(..args) = if DEBUG { /* debug logic */ }
#let debug-box(c) = if DEBUG { /* with borders */ } else { c }
#let debug-measure(c, ..) = if DEBUG { /* with overlay */ } else { c }
```

Or use conditional compilation:

```bash
# Compile with debug flag via CLI (requires wrapper)
typst compile document.typ --input debug=true
```

```typst
// In document
#let DEBUG = sys.inputs.at("debug", default: "false") == "true"
```
