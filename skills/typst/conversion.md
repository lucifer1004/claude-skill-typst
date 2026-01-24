# Converting Documents to Typst

For Typst language fundamentals (modes, types, functions), see [basics.md](basics.md).

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

### Headings

```typst
= Level 1 Heading
== Level 2 Heading
=== Level 3 Heading
==== Level 4 Heading
```

Or functional syntax:

```typst
#heading(level: 1)[Title]
#heading(level: 2, numbering: none)[Unnumbered]
```

### Lists

```typst
// Unordered
- First item
- Second item
  - Nested item

// Ordered
+ First item
+ Second item
  + Nested item

// Term list
/ Term: Definition
/ Another: Its definition
```

### Links and References

```typst
// External link
#link("https://example.com")[Click here]

// Internal reference
See @introduction for details.
= Introduction <introduction>

// Footnote
Text with footnote#footnote[Footnote content].
```

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

```typst
// Inline code
Use the `print` function.
```

Code block with language:

````typst
```python
def hello():
    print("Hello")
```
````

Raw block with language:

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
| `/`       | `\/`     | Comment       |
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

## Common Patterns

### Horizontal Rule

```typst
#line(length: 100%)
```

### Page Break

```typst
#pagebreak()
#pagebreak(weak: true)  // Only if not at page start
```

### Spacing

```typst
#v(1em)  // Vertical space
#h(1em)  // Horizontal space
#parbreak()  // Paragraph break
```

### Comments

```typst
// Single line comment

/* Multi-line
   comment */
```

## Using Pandoc for Conversion

Pandoc (since v2.18) supports Typst as an output format, enabling automated conversion from Markdown, LaTeX, and other formats.

### Basic Commands

```bash
# Markdown to Typst
pandoc -f markdown -t typst input.md -o output.typ

# LaTeX to Typst
pandoc -f latex -t typst input.tex -o output.typ

# Multiple formats to Typst
pandoc input.md input2.md -t typst -o combined.typ

# Markdown to PDF via Typst
pandoc input.md -o output.pdf --pdf-engine=typst
```

### Metadata Variables

Control output via YAML frontmatter or command-line `-V`:

```yaml
---
title: "Document Title"
author: "Author Name"
date: "2026-01-01"
papersize: a4
margin:
  x: 2cm
  y: 2.5cm
fontsize: 11pt
mainfont: "Libertinus Serif"
mathfont: "Libertinus Math"
codefont: "Fira Code"
section-numbering: "1.1"
page-numbering: "1"
columns: 1
linestretch: 1.25
linkcolor: "4183c4"
---
```

Or via command line:

```bash
pandoc input.md -t typst -o output.typ \
  -V papersize=a4 \
  -V fontsize=12pt \
  -V mainfont="Times New Roman"
```

### Available Variables

| Variable            | Description                                   | Example            |
| ------------------- | --------------------------------------------- | ------------------ |
| `title`             | Document title                                | `"My Report"`      |
| `author`            | Author name(s)                                | `"John Doe"`       |
| `date`              | Document date                                 | `"2024-01-01"`     |
| `papersize`         | Paper size                                    | `a4`, `letter`     |
| `margin`            | Page margins (x, y, top, bottom, left, right) | `2cm`              |
| `fontsize`          | Base font size                                | `11pt`             |
| `mainfont`          | Main text font                                | Font name          |
| `mathfont`          | Math font                                     | Font name          |
| `codefont`          | Code font                                     | Font name          |
| `section-numbering` | Heading number format                         | `"1.1"`, `"1.A.1"` |
| `page-numbering`    | Page number format                            | `"1"`, `"i"`       |
| `columns`           | Number of columns                             | `1`, `2`           |
| `linestretch`       | Line spacing multiplier                       | `1.5`              |
| `linkcolor`         | External link color (hex)                     | `"4183c4"`         |
| `citecolor`         | Citation link color (hex)                     | `"000000"`         |

### Custom Templates

Extract and modify the default template:

```bash
# Get default template
pandoc -D typst > my-template.typ

# Use custom template
pandoc input.md -t typst --template=my-template.typ -o output.typ
```

### Direct PDF Generation

```bash
# Basic PDF via Typst
pandoc input.md -o output.pdf --pdf-engine=typst

# With PDF/A-2b compliance (Typst 0.12+)
pandoc input.md -o output.pdf --pdf-engine=typst \
  --pdf-engine-opt=--pdf-standard=a-2b
```

### Known Limitations

1. **Citation handling**: `@ref` in Markdown becomes `#cite(<ref>)` in Typst. Escape with `\@` if literal `@` needed.

2. **Image sizing**: Default image dimensions may differ from other outputs. Specify width explicitly:

   ```markdown
   ![Alt text](image.png){width=80%}
   ```

3. **Complex tables**: Cell merging and advanced table features may need manual adjustment.

4. **Raw blocks**: Use raw Typst blocks for unsupported features:

   ````markdown
   ```{=typst}
   #set text(fill: red)
   Custom Typst code here.
   ```
   ````

### Workflow Example

```bash
# Convert with custom settings
pandoc document.md \
  -t typst \
  -o document.typ \
  -V papersize=a4 \
  -V mainfont="Libertinus Serif" \
  -V section-numbering="1.1" \
  --toc

# Compile to PDF
typst compile document.typ
```

## Best Practices

1. **Preserve semantics**: Map to equivalent Typst elements, not just visual appearance
2. **Use functions**: For repeated patterns, create helper functions
3. **Handle edge cases**: Empty content, special characters, nested structures
4. **Test incrementally**: Convert small sections and verify output
5. **Keep formatting minimal**: Let Typst defaults handle most styling
6. **Use Pandoc for bulk conversion**: Automate repetitive conversions with scripts
7. **Post-process Pandoc output**: Review and refine generated Typst code for complex documents
