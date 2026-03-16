# Academic Writing

For page layout, see [styling.md](styling.md). For reusable templates, see [template.md](template.md). For state and counters, see [advanced.md](advanced.md).

## Paper Structure

```typst
#set page(paper: "us-letter", margin: 1in)
#set text(font: "New Computer Modern", size: 12pt)
#set par(justify: true, leading: 0.65em, first-line-indent: 0.5in)
#set heading(numbering: "1.1")

// Title block
#align(center)[
  #text(17pt, weight: "bold")[Paper Title]
  #v(0.5em)
  Author Name \
  _Institution_ \
  #link("mailto:email@example.edu")
  #v(1em)
]

// Abstract
#heading(outlined: false, numbering: none)[Abstract]
#par(first-line-indent: 0pt)[
  This paper presents...
]
#v(1em)

// Body
= Introduction

The rest of the paper...
```

## Bibliography and Citations

### Setup

Place a `.bib` file (BibTeX or BibLaTeX format) in your project:

```typst
// At the end of your document
#bibliography("refs.bib")
```

### Citation Syntax

```typst
As shown by @smith2024.              // Smith (2024) — narrative
This was proven @smith2024.          // (Smith, 2024) — parenthetical
See @smith2024[pp. 12-15].           // (Smith, 2024, pp. 12-15) — with supplement
Multiple sources @smith2024 @doe2023.
```

### Citation Styles

```typst
#bibliography("refs.bib", style: "ieee")          // [1], [2], ...
#bibliography("refs.bib", style: "apa")            // (Author, Year)
#bibliography("refs.bib", style: "chicago-author-date")
#bibliography("refs.bib", style: "mla")
#bibliography("refs.bib", style: "chicago-notes")  // Footnote style
```

Full list: https://typst.app/docs/reference/model/bibliography/

### Bibliography Title

```typst
#bibliography("refs.bib", title: [References], style: "ieee")
#bibliography("refs.bib", title: none)   // No heading
```

### Multiple `.bib` Files

```typst
#bibliography(("primary.bib", "secondary.bib"), style: "apa")
```

## Equations

### Inline and Display Math

```typst
The equation $E = m c^2$ is well known.

The quadratic formula is:
$ x = (-b plus.minus sqrt(b^2 - 4 a c)) / (2 a) $
```

### Equation Numbering

```typst
#set math.equation(numbering: "(1)")

$ integral_0^infinity e^(-x^2) dif x = sqrt(pi) / 2 $ <eq:gaussian>

As shown in @eq:gaussian...
```

### Aligned Equations

```typst
$ a &= b + c \
  &= d + e + f $
```

## Theorem Environments

Typst has no built-in theorem environment, but you can build one with counters and show rules.

### Simple Theorem Block

```typst
#let theorem-counter = counter("theorem")

#let theorem(body, name: none) = {
  theorem-counter.step()
  block(
    width: 100%,
    inset: 10pt,
    stroke: (left: 2pt + black),
    {
      context {
        let num = theorem-counter.display()
        [*Theorem #num*]
        if name != none [ _(#name)_]
        [*.* ]
      }
      emph(body)
    },
  )
}

#theorem[Every even integer greater than 2 is the sum of two primes.]
#theorem(name: "Fermat's Last")[No three positive integers satisfy $a^n + b^n = c^n$ for $n > 2$.]
```

### Proof Block

```typst
#let proof(body) = block(
  width: 100%,
  inset: (left: 10pt),
  {
    [_Proof._ ]
    body
    h(1fr)
    $square$
  },
)

#proof[
  By contradiction, assume...
  Therefore the statement holds.
]
```

### Shared Counter for Theorem-Like Environments

```typst
#let thm-counter = counter("theorem")

#let make-env(kind) = (body, name: none) => {
  thm-counter.step()
  block(
    width: 100%,
    inset: 10pt,
    stroke: (left: 2pt + black),
    {
      context {
        let num = thm-counter.display()
        [*#kind #num*]
        if name != none [ _(#name)_]
        [*.* ]
      }
      if kind == "Theorem" or kind == "Lemma" { emph(body) } else { body }
    },
  )
}

#let theorem = make-env("Theorem")
#let lemma = make-env("Lemma")
#let definition = make-env("Definition")
#let corollary = make-env("Corollary")

#definition[A group is a set $G$ with a binary operation...]
#theorem[Every finite group of prime order is cyclic.]
#corollary[Every group of order 2 is isomorphic to $ZZ slash 2 ZZ$.]
```

### Chapter-Linked Numbering

```typst
#let thm-counter = counter("theorem")
#show heading.where(level: 1): it => {
  thm-counter.update(0)
  it
}

#let theorem(body) = {
  thm-counter.step()
  context {
    let ch = counter(heading).get().first()
    let n = thm-counter.get().first()
    block(
      width: 100%,
      inset: 10pt,
      stroke: (left: 2pt + black),
      [*Theorem #ch.#n.* ] + emph(body),
    )
  }
}
```

## Figure and Table Numbering

```typst
// Number figures as "Figure 1", tables as "Table 1"
#set figure(numbering: "1")

// Reference: "see Figure 1", "see Table 2"
#figure(table(columns: 2, [A], [B]), caption: [Sample data]) <tab:data>
See @tab:data for results.
```

### Supplemental Figures

```typst
#set figure.caption(separator: [. ])

#figure(
  image("plot.png", width: 80%),
  caption: [Results of experiment A],
  supplement: [Fig.],
) <fig:results>
```

For two-column layout and full-width elements in multi-column documents, see [styling.md](styling.md).

## Common Academic Patterns

| Pattern           | Code                                                                |
| ----------------- | ------------------------------------------------------------------- |
| Double spacing    | `#set par(leading: 1.3em)`                                          |
| Numbered sections | `#set heading(numbering: "1.1")`                                    |
| Running header    | `#set page(header: context { ... })` — see [styling.md](styling.md) |
| Abstract indent   | `#pad(x: 2em)[Abstract text...]`                                    |
| Keywords line     | `*Keywords:* word1, word2, word3`                                   |
| Acknowledgments   | `#heading(numbering: none)[Acknowledgments]`                        |
| Line numbers      | Not built-in — use `@preview/lineno` package                        |
| Footnotes         | `Text#footnote[Note content].` — auto-numbered                      |
| Subfigures        | Not built-in — use `@preview/subpar` package                        |
| Appendix          | See "Appendix" in [styling.md](styling.md)                          |
