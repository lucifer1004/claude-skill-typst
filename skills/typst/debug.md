# Typst Debugging Techniques

For language basics, see [basics.md](basics.md). For type inspection (`type()`, `repr()`), see [types.md](types.md). For state/context debugging, see [advanced.md](advanced.md).

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
