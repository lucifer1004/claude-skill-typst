// Styled Document Example
// Demonstrates: set rules, show rules, page layout, counters, headings, figures, labels, multi-region
// Compile: typst compile examples/styled-document.typ

// === Set Rules ===
#set document(title: "Styled Document Example", author: "Author Name")
#set text(size: 11pt, lang: "en")
#set par(justify: true)
#set heading(numbering: "1.1")

// === Show Rules ===
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  align(center, text(16pt, strong(it.body)))
  v(0.5em)
}

#show heading.where(level: 2): set text(size: 13pt)
#show link: set text(fill: blue)
#show raw: set text(size: 9pt)

// === Front Matter (Roman numerals) ===
#set page(paper: "a4", margin: 2cm, numbering: "i")

#align(center + horizon)[
  #text(24pt, strong[Styled Document Example])

  #v(1em)
  Author Name

  #v(0.5em)
  #datetime.today().display("[month repr:long] [day], [year]")
]

#pagebreak()

#outline(title: [Contents], indent: auto, depth: 3)
#pagebreak()

// === Main Matter (Arabic, reset counter) ===
#set page(
  numbering: "1",
  header: context {
    let page = counter(page).get().first()
    if page > 1 {
      [Styled Document Example #h(1fr) Page #page]
    }
  },
)
#counter(page).update(1)

= Introduction <intro>

This document demonstrates the styling patterns from `styling.md`: set rules, show rules, page layout with headers, heading numbering, figures with labels, and multi-region documents.

== Motivation

Typst uses *set rules* for defaults and *show rules* for transformations. This separation keeps documents clean and maintainable.

== Scope

See @results for the main content and @fig:demo for a sample figure.

= Results <results>

Here we demonstrate figures, labels, and references working together.

#figure(
  table(
    columns: 3,
    [*Item*], [*Value*], [*Unit*],
    [Length], [42], [cm],
    [Width], [18], [cm],
    [Height], [7], [cm],
  ),
  caption: [Sample measurements],
) <fig:demo>

As shown in @fig:demo, the table uses standard Typst formatting. For more details, refer back to @intro.

== Additional Notes

Built-in counters track pages and headings automatically:

- Current page: #context counter(page).display()
- Current heading: #context counter(heading).display()

// === Appendix ===
#counter(heading).update(0)
#set heading(numbering: "A.1")

= Appendix

Supporting material goes here. The heading numbering switches to letter-based format for appendix sections.

== Data Sources

All measurements in @fig:demo are illustrative.
