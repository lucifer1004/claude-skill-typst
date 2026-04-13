# Converting Documents to Typst

For Typst language fundamentals (modes, functions), see [basics.md](basics.md). For types and operators, see [types.md](types.md). For advanced table features, see [tables.md](tables.md).

## Basic Formatting

| Effect    | Markdown      | LaTeX              | Typst                |
| --------- | ------------- | ------------------ | -------------------- |
| Bold      | `**text**`    | `\textbf{text}`    | `*text*`             |
| Italic    | `*text*`      | `\textit{text}`    | `_text_`             |
| Code      | `` `code` ``  | `\texttt{code}`    | `` `code` ``         |
| Link      | `[text](url)` | `\href{url}{text}` | `#link("url")[text]` |
| Heading   | `# Title`     | `\section{Title}`  | `= Title`            |
| List item | `- item`      | `\item item`       | `- item`             |
| Numbered  | `1. item`     | `\item item`       | `+ item`             |

For full Typst syntax details on headings, lists, links, and references, see [basics.md](basics.md).

## Math Conversion

### Inline vs Display Math

```typst
// Inline math
The formula $a + b = c$ is simple.

// Display math
$ integral_0^infinity e^(-x) dif x = 1 $
```

### Common Conversions

| LaTeX            | Typst          |
| ---------------- | -------------- |
| `\frac{a}{b}`    | `frac(a, b)`   |
| `\sqrt{x}`       | `sqrt(x)`      |
| `\sum_{i=1}^{n}` | `sum_(i=1)^n`  |
| `\int_a^b`       | `integral_a^b` |
| `\alpha, \beta`  | `alpha, beta`  |
| `\mathbf{x}`     | `bold(x)`      |
| `\text{word}`    | `"word"`       |
| `\left( \right)` | `lr(( ))`      |
| `\begin{matrix}` | `mat(...)`     |
| `\begin{cases}`  | `cases(...)`   |

### Math Examples

```typst
// Fraction
$ frac(a + b, c) $

// Matrix
$ mat(1, 2; 3, 4) $

// Cases
$ f(x) = cases(
  x^2 "if" x > 0,
  0 "otherwise"
) $

// Aligned equations
$ a &= b + c \
  &= d + e $
```

### Using mitex for LaTeX Math

For complex LaTeX math, use the mitex package:

```typst
#import "@preview/mitex:0.2.6": mitex, mi

// Display math
#mitex(`\frac{\partial f}{\partial x}`)

// Inline math
The value is #mi(`\alpha + \beta`).
```

## Code Blocks

Inline code uses backticks (same as Markdown). Fenced code blocks use triple backticks with language name. For programmatic raw content:

```typst
#raw("print('hello')", lang: "python", block: true)
```

## Tables

```typst
#table(
  columns: (auto, 1fr, 1fr),
  align: (left, center, right),

  // Header row
  [*Name*], [*Value*], [*Unit*],

  // Data rows
  [Length], [10], [cm],
  [Width], [5], [cm],
)
```

### From Markdown Tables

Markdown:

```markdown
| Name | Value |
| ---- | ----- |
| A    | 1     |
| B    | 2     |
```

Typst:

```typst
#table(
  columns: 2,
  [*Name*], [*Value*],
  [A], [1],
  [B], [2],
)
```

## Figures and Images

```typst
#figure(
  image("diagram.png", width: 80%),
  caption: [A diagram showing the process],
) <fig:diagram>

// Reference
See @fig:diagram for details.
```

## Block Elements

### Quotes

```typst
#quote(block: true)[
  To be or not to be.
]

// With attribution
#quote(block: true, attribution: [Shakespeare])[
  To be or not to be.
]
```

### Admonitions / Callouts

```typst
// Simple box
#block(
  fill: luma(240),
  inset: 1em,
  radius: 4pt,
)[
  *Note:* Important information here.
]

// Custom admonition function
#let note(body) = block(
  fill: rgb("#e8f4f8"),
  inset: 1em,
  radius: 4pt,
  width: 100%,
)[*Note:* #body]

#note[Remember to save your work.]
```

## Escaping Rules

### Special Characters

Characters requiring escape with backslash:

| Character | Escape   | Purpose       |
| --------- | -------- | ------------- |
| `*`       | `\*`     | Bold marker   |
| `_`       | `\_`     | Italic marker |
| `#`       | `\#`     | Code mode     |
| `$`       | `\$`     | Math mode     |
| `@`       | `\@`     | Reference     |
| `<`       | `\<`     | Label start   |
| `>`       | `\>`     | Label end     |
| `/`       | `\/`     | Term list     |
| `` ` ``   | `` \` `` | Raw text      |
| `\`       | `\\`     | Escape char   |

### In Raw Strings

Inside `#raw("...")`, only escape:

- `\` → `\\`
- `"` → `\"`

```typst
#raw("path\\to\\file", lang: "text")
```

## Document Structure

### From LaTeX

LaTeX:

```latex
\documentclass{article}
\title{My Document}
\author{Author Name}
\begin{document}
\maketitle
\section{Introduction}
Content here.
\end{document}
```

Typst:

```typst
#set document(title: "My Document", author: "Author Name")
#set page(paper: "a4")

#align(center, text(20pt)[*My Document*])
#align(center)[Author Name]

= Introduction
Content here.
```

### From Markdown

Markdown:

```markdown
---
title: My Document
author: Author Name
---

# Introduction

Some **bold** and _italic_ text.

- List item 1
- List item 2
```

Typst:

```typst
#set document(title: "My Document", author: "Author Name")

= Introduction

Some *bold* and _italic_ text.

- List item 1
- List item 2
```

## Using Pandoc for Conversion

Pandoc (since v2.18) supports Typst as an output format.

```bash
pandoc -f markdown -t typst input.md -o output.typ    # Markdown → Typst
pandoc -f latex -t typst input.tex -o output.typ       # LaTeX → Typst
pandoc input.md -o output.pdf --pdf-engine=typst        # Markdown → PDF via Typst
```

### Common Options

```bash
pandoc input.md -t typst -o output.typ \
  -V papersize=a4 -V fontsize=12pt -V mainfont="Libertinus Serif" \
  -V section-numbering="1.1" --toc
```

Key `-V` variables: `title`, `author`, `papersize`, `margin`, `fontsize`, `mainfont`/`mathfont`/`codefont`, `section-numbering`, `page-numbering`, `columns`, `linestretch`, `linkcolor`. These can also be set via YAML frontmatter.

Custom templates: `pandoc -D typst > template.typ`, then `pandoc input.md --template=template.typ -o output.typ`.

### Known Limitations

- **Citations**: `@ref` in Markdown → `#cite(<ref>)` in Typst. Escape literal `@` with `\@`.
- **Complex tables**: Cell merging needs manual adjustment.
- **Raw Typst blocks**: Use ```` ```{=typst} ```` fenced blocks for unsupported features.

Review and refine Pandoc output — custom styling and advanced layout usually need manual adjustment.
