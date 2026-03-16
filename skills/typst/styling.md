# Styling and Layout

For language basics (syntax, functions), see [basics.md](basics.md). For data types and operators, see [types.md](types.md). For reusable template creation, see [template.md](template.md).

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

## Built-in Counters

```typst
#context counter(page).display()    // Current page
#counter(page).update(1)            // Reset to 1
#context counter(heading).display() // Heading number
```

For custom counters and state tracking, see [advanced.md](advanced.md).

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
```

For per-chapter numbering, see [template.md](template.md).

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

To query labels programmatically, see the Query System in [advanced.md](advanced.md).

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

## Multi-Column Layout

```typst
// Whole document
#set page(columns: 2)

// Specific section
#columns(2, gutter: 12pt)[
  First column text...
  #colbreak()
  Second column text...
]
```

### Full-Width Element in Two-Column

```typst
#set page(columns: 2)

#place(top + center, scope: "parent", float: true)[
  #figure(
    image("wide-figure.png", width: 100%),
    caption: [Wide figure spanning both columns],
  )
]
```

## Quick Patterns

| Pattern         | Code                                                |
| --------------- | --------------------------------------------------- |
| Title page      | `#align(center + horizon)[...]` then `#pagebreak()` |
| Bibliography    | `#bibliography("refs.bib", style: "ieee")`          |
| Horizontal rule | `#line(length: 100%)`                               |
