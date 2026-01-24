// Basic Typst Document Example
// Demonstrates: document setup, headings, lists, math, code, figures

// === Document Settings ===
#set document(title: "Basic Document", author: "Author Name")
#set page(paper: "a4", margin: 2cm, numbering: "1")
#set text(font: "Libertinus Serif", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.1")

// === Title Page ===
#align(center + horizon)[
  #text(24pt, weight: "bold")[Basic Document]
  #v(2em)
  #text(14pt)[Author Name]
  #v(1em)
  #datetime.today().display()
]
#pagebreak()

// === Table of Contents ===
#outline(title: [Contents], indent: auto, depth: 2)
#pagebreak()

// === Content ===

= Introduction

This document demonstrates basic Typst features. Typst is a modern typesetting
system with a simple syntax and fast compilation.

== Text Formatting

Basic formatting: *bold text*, _italic text_, and `inline code`.

You can also use #strong[functional syntax] for #emph[emphasis].

== Lists

Unordered list:
- First item
- Second item
  - Nested item
  - Another nested

Ordered list:
+ Step one
+ Step two
+ Step three

Term list:
/ Typst: A modern typesetting system
/ LaTeX: A traditional typesetting system

= Mathematics

== Inline Math

The quadratic formula is $x = (-b plus.minus sqrt(b^2 - 4a c)) / (2a)$.

== Display Math

The Gaussian integral:

$ integral_(-infinity)^infinity e^(-x^2) dif x = sqrt(pi) $

A matrix example:

$
  mat(
    1, 2, 3;
    4, 5, 6;
    7, 8, 9
  )
$

= Code

Python example:

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))  # Output: 55
```

= Figures and Tables

== Figure

#figure(
  rect(width: 6cm, height: 4cm, fill: luma(230), radius: 4pt)[
    #align(center + horizon)[Placeholder Image]
  ],
  caption: [A sample figure with caption.],
) <fig:sample>

Reference: See @fig:sample for the sample figure.

== Table

#figure(
  table(
    columns: 3,
    align: (left, center, right),
    stroke: 0.5pt,
    [*Name*], [*Value*], [*Unit*],
    [Length], [10.5], [cm],
    [Width], [5.2], [cm],
    [Height], [3.8], [cm],
  ),
  caption: [Sample measurements],
) <tab:measurements>

= Conclusion

This document covered the essential Typst features:
- Document and page setup
- Text formatting and lists
- Mathematical formulas
- Code blocks with syntax highlighting
- Figures and tables with captions

For more advanced features, see the template and package examples.
