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

## From LaTeX: Package and Concept Map

Typst is "batteries included" — most common LaTeX packages are built in:

| LaTeX package            | Typst equivalent                                            |
| ------------------------ | ----------------------------------------------------------- |
| `graphicx`, `svg`        | `image()` function                                          |
| `tabularx`, `tabularray` | `table()`, `grid()`                                         |
| `amsmath`, `amssymb`     | Built into math mode; see [academic.md](academic.md)        |
| `hyperref`               | `link()` function                                           |
| `biblatex`, `natbib`     | `cite()`, `bibliography()` — see [academic.md](academic.md) |
| `geometry`, `fancyhdr`   | `#set page(margin: ..., header: ..., footer: ...)`          |
| `xcolor`                 | `#set text(fill: rgb("#..."))`, `luma()`, etc.              |
| `babel`, `polyglossia`   | `#set text(lang: "zh")`                                     |
| `lstlisting`, `minted`   | `raw()` function, ` ` ` ` markup                            |
| `caption`                | `figure(caption: ...)`                                      |
| `enumitem`               | `list()`, `enum()`, `terms()` parameters                    |
| `parskip`                | `#set par(spacing: ..., first-line-indent: ...)`            |
| `nicefrac`               | `frac(a, b, style: "horizontal")` or `"skewed"`             |
| `csquotes`               | Smart quotes auto-active; set `text(lang: ...)`             |

### Concept mappings

| LaTeX                             | Typst                                         |
| --------------------------------- | --------------------------------------------- |
| `\documentclass{article}`         | `#show: template.with(...)` (from a template) |
| `\newcommand{\foo}{...}`          | `#let foo = ...` or `#let foo(x) = ...`       |
| `\textbf{x}` (style-only, no tag) | `#text(weight: "bold")[x]` — style only       |
| Semantic strong emphasis          | `*x*` or `#strong[x]` — tagged for a11y       |
| `\bfseries` (declaration-style)   | `#set text(weight: "bold")` in current scope  |
| `\textsc{x}`                      | `#smallcaps[x]`                               |
| `\left( ... \right)`              | Auto-scaling in math; use `lr(( ))` to force  |
| `\label{foo}` / `\ref{foo}`       | `<foo>` / `@foo`                              |

Set rules act like LaTeX declarations scoped to the current block; direct function calls act like argument-style commands.

### "LaTeX look" starter

Reproduces the Computer Modern / justified / tight-leading look of a classic LaTeX article:

```typst
#set page(margin: 1.75in)
#set par(leading: 0.55em, spacing: 0.55em, first-line-indent: 1.8em, justify: true)
#set text(font: "New Computer Modern")
#show raw: set text(font: "New Computer Modern Mono")
#show heading: set block(above: 1.4em, below: 1em)
```

## Math Conversion

Inline math: `$a + b = c$`. Display math (spaced dollar signs): `$ integral_0^infinity e^(-x) dif x = 1 $`.

| LaTeX                           | Typst                                                       |
| ------------------------------- | ----------------------------------------------------------- |
| `\frac{a}{b}`                   | `frac(a, b)`                                                |
| `\sqrt{x}`                      | `sqrt(x)`                                                   |
| `\sum_{i=1}^{n}`                | `sum_(i=1)^n`                                               |
| `\int_a^b`                      | `integral_a^b`                                              |
| `\alpha, \beta`                 | `alpha, beta`                                               |
| `\mathbf{x}`                    | `bold(x)`                                                   |
| `\text{word}`                   | `"word"`                                                    |
| `\left( \right)`                | auto (use `lr(( ))` to force)                               |
| `\begin{matrix}`                | `mat(...)`                                                  |
| `\begin{cases}`                 | `cases(...)`                                                |
| `\citet{key}`, `\textcite{key}` | `#cite(<key>, form: "prose")`                               |
| `\arrow`, alt forms             | `arrow.r.squiggly`, `arrow.l.long`, etc. (symbol modifiers) |

### Sub/superscript gotcha when porting

Transcribing `\alpha_c(N=40)` verbatim gives `alpha_c(N=40)`, which Typst reads
as subscript `c(N=40)` — a `(` right after a letter/string script is swallowed
as a function call. Put a space before the paren: `alpha_c (N=40)`. This is one
of several silent LaTeX→Typst math traps (fractions, `"--"`, en-dashes); see
[debug.md](debug.md) ("Common Errors & Symbol Gotchas") for the full list, and
[academic.md](academic.md) (Equations) for the authoring-path cheat sheet.

### Using mitex for LaTeX Math

For complex LaTeX math, use the mitex package:

```typst
#import "@preview/mitex:0.2.6": mitex, mi

#mitex(`\frac{\partial f}{\partial x}`)   // display math
The value is #mi(`\alpha + \beta`).        // inline math
```

## Code Blocks

Inline code uses backticks (same as Markdown). Fenced blocks use triple backticks with a language name. For programmatic raw content:

```typst
#raw("print('hello')", lang: "python", block: true)
```

## Tables

Markdown tables have no direct markup equivalent; use `table()`:

```typst
#table(
  columns: (auto, 1fr),
  [*Name*], [*Value*],   // header row
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

See @fig:diagram for details.
```

## Block Elements

```typst
// Quote with attribution
#quote(block: true, attribution: [Shakespeare])[To be or not to be.]

// Admonition / callout via a custom function
#let note(body) = block(
  fill: rgb("#e8f4f8"),
  inset: 1em,
  radius: 4pt,
  width: 100%,
)[*Note:* #body]

#note[Remember to save your work.]
```

## Escaping Rules

Characters requiring escape with backslash in markup:

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

Inside `#raw("...")` strings, only escape `\` → `\\` and `"` → `\"`.

## Document Structure

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

## Current Limitations vs LaTeX

- **Plotting ecosystem**: LaTeX has mature PGF/TikZ. Typst's `cetz` is catching up but narrower. See [package search](scripts/search-packages.py) for alternatives.
- **Mid-page margin changes**: `#set page(margin: ...)` forces a page break. For local stretching, use `pad()` with negative padding.
- **Change bars / track-changes workflows**: No first-class equivalent yet.
- **`\input` with partial scope**: Typst `include` evaluates a whole file; scoping differs from TeX's `\input`.
- **Some niche journal templates** may not yet be on Typst Universe — check before committing a submission to Typst-only.

## Using Pandoc for Conversion

Pandoc (since v2.18) supports Typst output:

```bash
pandoc -f markdown -t typst input.md -o output.typ      # Markdown → Typst
pandoc -f latex -t typst input.tex -o output.typ        # LaTeX → Typst
pandoc input.md -o output.pdf --pdf-engine=typst        # Markdown → PDF via Typst
```

Key `-V` variables: `title`, `author`, `papersize`, `fontsize`, `mainfont`/`mathfont`/`codefont`, `section-numbering`, `page-numbering`, `columns`, `linestretch`, `linkcolor`. Custom templates: `pandoc -D typst > template.typ`, then `--template=template.typ`.

Known limitations: Markdown `@ref` becomes `#cite(<ref>)` (escape literal `@` as `\@`); cell merging in complex tables needs manual work; use ```` ```{=typst} ```` fenced blocks for unsupported features. Always review Pandoc output — custom styling and advanced layout need manual adjustment.
