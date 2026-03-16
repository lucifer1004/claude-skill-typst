# Typst Template Development

For set/show rules, page layout, and other styling basics, see [styling.md](styling.md). For publishing as a package, see [package.md](package.md).

**Complete example**: See [examples/template-report.typ](examples/template-report.typ) for a full template with headers, custom counters, note boxes, and multi-region document.

## Template Function Pattern

A template wraps content with styling and layout:

```typst
#let template(title: none, author: none, body) = {
  set document(
    title: if title != none { title } else { "" },
    author: if author != none { (author,) } else { () },
  )
  set page(paper: "a4", margin: 2cm)
  set text(font: "Libertinus Serif", size: 11pt)
  body
}

// Usage
#show: template.with(title: "My Document")
```

## Configuration Pattern

Expose options via named parameters with sensible defaults:

```typst
#let template(
  title: none,
  author: none,
  font: "Libertinus Serif",
  font-size: 11pt,
  paper: "a4",
  lang: "en",
  body,
) = {
  set document(title: title, author: author)
  set page(paper: paper)
  set text(font: font, size: font-size, lang: lang)

  if title != none {
    align(center, text(20pt, strong(title)))
    if author != none { align(center, author) }
    v(2em)
  }

  body
}
```

For advanced configuration with dictionary merging:

```typst
#let default-config = (
  color: blue,
  size: 12pt,
  inset: 1em,
)

#let configure(..overrides) = {
  let cfg = default-config
  for (k, v) in overrides.named() { cfg.insert(k, v) }
  cfg
}
```

## Template with Show Rules

Templates can include show rules for consistent element styling:

```typst
#let report(title: none, body) = {
  set page(paper: "a4", margin: 2cm, numbering: "1")
  set text(size: 11pt)
  set heading(numbering: "1.1")

  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    align(center, text(18pt, strong(it.body)))
    v(1em)
  }

  show link: set text(fill: blue)

  body
}
```

## Per-Chapter Figure Numbering

```typst
#set figure(numbering: num => context {
  let ch = counter(heading.where(level: 1)).get().first()
  [#ch.#num]
})
```

## Query in Templates

Templates often use `query()` to build dynamic elements like TOCs or running headers:

```typst
#let template(body) = {
  set page(header: context {
    let headings = query(heading.where(level: 1))
    let here-loc = here().position()
    let before = headings.filter(h => h.location().position().y < here-loc.y)
    if before.len() > 0 { before.last().body }
  })

  body
}
```

For detailed query and state patterns, see [advanced.md](advanced.md).

## Testing Templates

1. **Compile with minimal content**: Catch missing defaults early

   ```bash
   echo '#show: template.with()' > test.typ && typst compile test.typ
   ```

2. **Test edge cases**: Empty body, very long titles, single-page vs multi-page

3. **Verify text output**: Use `pdftotext` since agents cannot preview PDFs

   ```bash
   typst compile test.typ && pdftotext test.pdf - | head -20
   ```

4. **Check with debug tools**: See [debug.md](debug.md) for `repr()`, `measure()`, and visual boundary helpers

## Best Practices

1. **Sensible defaults** for every parameter — the template should produce reasonable output with zero configuration

2. **Configuration over hardcoding** — expose colors, fonts, sizes as parameters

3. **Document the API** — use `///` doc comments on the template function

4. Provide a **complete example** showing all parameters in use

5. Keep **set rules** and **show rules** inside the template function so users get a clean namespace

6. Use **context** sparingly — it adds complexity and makes templates harder to debug

7. Test with `--input` flags for conditional features:

   ```typst
   #let draft = sys.inputs.at("draft", default: "false") == "true"
   ```
