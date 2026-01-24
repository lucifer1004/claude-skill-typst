// Reusable Report Template Example
// Demonstrates: template function, set/show rules, counter, state, multi-region document

// === Template Definition ===

#let report(
  title: none,
  author: none,
  date: datetime.today(),
  abstract: none,
  body,
) = {
  // Document metadata
  set document(title: title, author: author)

  // Page setup with dynamic header
  set page(
    paper: "a4",
    margin: (top: 2.5cm, bottom: 2cm, x: 2cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        text(size: 9pt, fill: luma(100))[
          #title
          #h(1fr)
          Page #page-num
        ]
        v(-0.3em)
        line(length: 100%, stroke: 0.5pt + luma(200))
      }
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        align(center, text(size: 9pt)[#page-num])
      }
    },
  )

  // Text and paragraph settings
  set text(font: "Libertinus Serif", size: 11pt, lang: "en")
  set par(justify: true, leading: 0.65em)

  // Heading settings
  set heading(numbering: "1.1")

  // === Show Rules ===

  // Level 1 heading: page break + centered
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(1em)
    text(16pt, weight: "bold")[
      #if it.numbering != none {
        counter(heading).display()
        h(0.5em)
      }
      #it.body
    ]
    v(0.8em)
  }

  // Level 2 heading
  show heading.where(level: 2): it => {
    v(0.8em)
    text(13pt, weight: "bold")[
      #if it.numbering != none {
        counter(heading).display()
        h(0.5em)
      }
      #it.body
    ]
    v(0.5em)
  }

  // Figure caption styling
  show figure.caption: it => text(size: 9pt, style: "italic", it)

  // Link styling
  show link: it => text(fill: rgb("#2563eb"), it)

  // === Title Page ===
  align(center + horizon)[
    #text(28pt, weight: "bold")[#title]
    #v(3em)
    #text(14pt)[#author]
    #v(1.5em)
    #text(12pt, fill: luma(100))[#date.display(
      "[month repr:long] [day], [year]",
    )]
  ]
  pagebreak()

  // === Abstract (if provided) ===
  if abstract != none {
    heading(level: 1, numbering: none)[Abstract]
    text(style: "italic")[#abstract]
    pagebreak()
  }

  // === Table of Contents ===
  heading(level: 1, numbering: none)[Contents]
  outline(title: none, indent: auto, depth: 2)
  pagebreak()

  // === Main Content ===
  body
}

// === Custom Components ===

/// Note box with customizable type
#let note(body, type: "info") = {
  let styles = (
    info: (fill: rgb("#e0f2fe"), border: rgb("#0ea5e9")),
    warning: (fill: rgb("#fef3c7"), border: rgb("#f59e0b")),
    error: (fill: rgb("#fee2e2"), border: rgb("#ef4444")),
  )
  let style = styles.at(type, default: styles.info)

  block(
    fill: style.fill,
    stroke: (left: 3pt + style.border),
    inset: 1em,
    width: 100%,
  )[#body]
}

/// Example counter and block
#let example-counter = counter("example")

#let example(body) = {
  example-counter.step()
  block(
    fill: luma(245),
    inset: 1em,
    radius: 4pt,
    width: 100%,
  )[
    *Example #context example-counter.display():*
    #v(0.3em)
    #body
  ]
}

// ============================================================
// Usage: Apply the template
// ============================================================

#show: report.with(
  title: "Technical Report Template",
  author: "Research Team",
  abstract: [
    This document demonstrates a reusable Typst template with custom styling,
    dynamic headers, and helper functions. It serves as a starting point for
    technical reports, papers, and documentation.
  ],
)

= Introduction

This template provides a professional layout for technical documents. It includes:
- Automatic page numbering with headers
- Styled headings at multiple levels
- Custom note boxes and example blocks
- Figure and table formatting

#note[
  This is an informational note. Use it to highlight important information.
]

== Motivation

Typst offers a simpler alternative to LaTeX while maintaining professional output quality.

== Document Structure

The template automatically generates:
+ Title page with metadata
+ Abstract section (optional)
+ Table of contents
+ Numbered sections

= Features

== Note Boxes

Different types of notes for various purposes:

#note(type: "info")[
  *Info:* General information for the reader.
]

#note(type: "warning")[
  *Warning:* Something to be careful about.
]

#note(type: "error")[
  *Error:* Critical issues or common mistakes.
]

== Examples

The `example` function provides numbered examples:

#example[
  Calculate $integral_0^1 x^2 dif x$:
  $ integral_0^1 x^2 dif x = [x^3 / 3]_0^1 = 1/3 $
]

#example[
  Solve $x^2 - 5x + 6 = 0$:
  $ x = (5 plus.minus sqrt(25 - 24)) / 2 = (5 plus.minus 1) / 2 $
  Therefore $x = 3$ or $x = 2$.
]

== Figures

#figure(
  rect(width: 8cm, height: 5cm, fill: luma(240), radius: 4pt)[
    #align(center + horizon)[Architecture Diagram]
  ],
  caption: [System architecture overview],
) <fig:arch>

As shown in @fig:arch, the system consists of multiple components.

== Tables

#figure(
  table(
    columns: 4,
    align: (left, center, center, center),
    stroke: 0.5pt,
    [*Method*], [*Precision*], [*Recall*], [*F1*],
    [Baseline], [0.82], [0.78], [0.80],
    [Proposed], [0.91], [0.89], [0.90],
    [Enhanced], [0.94], [0.92], [0.93],
  ),
  caption: [Performance comparison of different methods],
)

= Conclusion

This template demonstrates key Typst features for document creation:
- Template functions with parameters
- Set and show rules for styling
- Custom counters for numbered elements
- Reusable component functions

Customize this template by modifying the `report` function parameters and styles.

// === Appendix ===
#counter(heading).update(0)
#set heading(numbering: "A.1")

= Appendix: Additional Notes

Appendices use letter numbering (A.1, A.2, etc.) by resetting the heading counter
and changing the numbering format.

== Configuration Options

The template supports these parameters:
- `title`: Document title (required)
- `author`: Author name(s)
- `date`: Publication date (defaults to today)
- `abstract`: Optional abstract content
