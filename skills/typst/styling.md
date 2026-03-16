# Styling and Layout

For language basics (syntax, types, functions), see [basics.md](basics.md). For reusable template creation, see [template.md](template.md).

## Set Rules

Configure element defaults:

```typst
#set page(paper: "a4", margin: (top: 2.5cm, bottom: 2cm, x: 2cm), numbering: "1")
#set text(font: "Libertinus Serif", size: 11pt, lang: "en")
#set par(justify: true, leading: 0.65em, first-line-indent: 1em)
#set heading(numbering: "1.1")
#set list(indent: 1em, marker: [•])
#set enum(indent: 1em, numbering: "1.")
#set figure(placement: auto, gap: 1em)
```

## Show Rules

Transform how elements are rendered.

### Show-Set (Targeted Styling)

```typst
#show heading: set text(font: "Helvetica")
#show heading.where(level: 1): set align(center)
#show raw: set text(font: "Fira Code", size: 9pt)
#show link: set text(fill: blue)
```

### Show-Transform (Custom Rendering)

```typst
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  align(center, text(18pt, strong(it.body)))
  v(1em)
}

#show figure.caption: it => text(size: 9pt, style: "italic", it)
```

## Page Layout

### Headers and Footers

```typst
#set page(
  header: context {
    let page = counter(page).get().first()
    if page > 1 { [Title #h(1fr) Page #page] }
  },
  footer: context { align(center, counter(page).display()) },
)
```

### Page Breaks

```typst
#pagebreak()              // Force page break
#pagebreak(weak: true)    // Only if not at page start
#pagebreak(to: "odd")     // Break to next odd page
```

## Counters

### Built-in Counters

```typst
#context counter(page).display()    // Current page
#counter(page).update(1)            // Reset to 1
#context counter(heading).display() // Heading number
```

### Custom Counters

```typst
#let example-counter = counter("example")

#let example(body) = {
  example-counter.step()
  block[*Example #context example-counter.display():* #body]
}
```

### State for Headers

```typst
#let chapter-title = state("chapter", none)

#show heading.where(level: 1): it => {
  chapter-title.update(it.body)
  it
}

#set page(header: context { chapter-title.get() })
```

For advanced state/context patterns, see [advanced.md](advanced.md).

## Heading Customization

### Numbering Formats

```typst
#set heading(numbering: "1.1")   // 1.1, 1.2, ...
#set heading(numbering: "1.a")   // 1.a, 1.b, ...
#set heading(numbering: "I.1")   // I.1, I.2, ...
```

### Outline (Table of Contents)

```typst
#outline(title: [Contents], indent: auto, depth: 3)
```

## Figure Customization

```typst
#set figure(numbering: "1")

// Per-chapter numbering
#set figure(numbering: num => context {
  let ch = counter(heading.where(level: 1)).get().first()
  [#ch.#num]
})
```

## Labels and References

### Creating Labels

```typst
= Introduction <intro>

#figure(image("fig.png"), caption: [A figure]) <fig:main>
```

### Programmatic Labels

```typst
// Create label from string
#let key = "my-key"
#[Some content #label("ref-" + key)]

// Reference with link
#link(label("ref-" + key))[See here]
```

### Querying Labels

```typst
#context {
  let target = query(label("ref-mykey"))
  if target.len() > 0 {
    [Found at page #target.first().location().page()]
  }
}
```

## Multi-Region Documents

### Front/Main Matter

```typst
// Front matter: Roman numerals
#set page(numbering: "i")
#outline()
#pagebreak()

// Main matter: Arabic, reset counter
#set page(numbering: "1")
#counter(page).update(1)
```

### Appendix

```typst
#counter(heading).update(0)
#set heading(numbering: "A.1")
```

## Quick Patterns

| Pattern         | Code                                                |
| --------------- | --------------------------------------------------- |
| Title page      | `#align(center + horizon)[...]` then `#pagebreak()` |
| Two columns     | `#set page(columns: 2)` or `#columns(2)[...]`       |
| Bibliography    | `#bibliography("refs.bib", style: "ieee")`          |
| Horizontal rule | `#line(length: 100%)`                               |

## Best Practices

1. **Set rules** for defaults, **show rules** for transformations
2. Use **context** sparingly — it adds complexity
3. Test edge cases: empty content, long titles, many pages
