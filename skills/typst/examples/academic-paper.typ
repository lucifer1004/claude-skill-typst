// Academic paper demonstrating built-in features.
// Compile: typst compile examples/academic-paper.typ

#set page(paper: "us-letter", margin: 1in, numbering: "1")
#set text(font: "New Computer Modern", size: 12pt)
#set par(justify: true, leading: 0.65em, first-line-indent: 0.5in)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")

// --- Theorem environments ---

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

// --- Title block ---

#align(center)[
  #text(17pt, weight: "bold")[On the Properties of Example Numbers]
  #v(0.5em)
  Jane Doe #h(2em) John Smith \
  _University of Typst_ \
  #v(0.3em)
  #text(size: 10pt, style: "italic")[March 2025]
  #v(1em)
]

// --- Abstract ---

#heading(outlined: false, numbering: none)[Abstract]
#par(first-line-indent: 0pt)[
  We investigate the properties of example numbers and demonstrate several
  foundational results. Our main contribution is a proof that all example
  numbers are positive, along with a classification theorem. We present
  supporting data in tabular form and discuss implications.
]
#v(0.5em)
*Keywords:* example numbers, positivity, classification
#v(1em)

// --- Body ---

= Introduction

#par(first-line-indent: 0pt)[
  Example numbers arise naturally in the study of
  typesetting systems. In this paper we establish their basic properties
  and present a classification.
]

The fundamental equation governing example numbers is:
$ E(n) = sum_(k=1)^n k^2 = (n(n+1)(2n+1)) / 6 $ <eq:sum>

As shown in @eq:sum, the sum grows cubically.

= Definitions and Preliminaries

#definition[
  An _example number_ is a positive integer $n$ such that $E(n) > n$.
]

#lemma[
  For all $n >= 1$, we have $E(n) >= 1$.
]

#proof[
  Since $E(n) = sum_(k=1)^n k^2$ and each term $k^2 >= 1$, the sum
  contains at least one positive term. Thus $E(n) >= 1^2 = 1$.
]

= Main Results

#theorem(name: "Positivity")[
  Every example number is positive.
]

#proof[
  By definition, an example number $n$ satisfies $E(n) > n > 0$.
  Therefore $n$ is positive.
]

We summarize the first several values in @tab:values.

#figure(
  table(
    columns: (1fr, 1fr, 1fr),
    align: (center, center, center),
    table.header([*$n$*], [*$E(n)$*], [*Example?*]),
    [1], [1], [No],
    [2], [5], [Yes],
    [3], [14], [Yes],
    [4], [30], [Yes],
    [5], [55], [Yes],
  ),
  caption: [Values of $E(n)$ for small $n$.],
) <tab:values>

= Discussion

The data in @tab:values confirms that most small integers are
example numbers. The sole exception is $n = 1$, where $E(1) = 1 = n$.

A natural question is whether the density of example numbers
approaches 1. We leave this as an open problem.

== Future Work

- Extend the classification to negative integers.
- Investigate connections to other number-theoretic sequences.

// --- Acknowledgments ---

#heading(numbering: none)[Acknowledgments]

The authors thank the Typst community for helpful discussions.

// --- Appendix ---

#pagebreak()
#counter(heading).update(0)
#set heading(numbering: "A.1")

= Proof Details

== Extended Computation

For completeness, we verify @eq:sum for $n = 5$:
$ E(5) = 1 + 4 + 9 + 16 + 25 = 55 = (5 dot 6 dot 11) / 6 $

This confirms the closed-form expression.
