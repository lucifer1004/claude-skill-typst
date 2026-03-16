// Table features showcase.
// Compile: typst compile examples/tables-showcase.typ

#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt)

= Tables Showcase

== Basic Table

#table(
  columns: 3,
  [*Name*], [*Age*], [*City*],
  [Alice], [30], [Berlin],
  [Bob], [25], [Tokyo],
  [Carol], [28], [Paris],
)

== Column Sizing

#table(
  columns: (auto, 1fr, 2fr),
  inset: 8pt,
  [*Label*], [*Description*], [*Details*],
  [A], [Short], [This column gets twice the remaining space],
  [B], [Medium], [Fractional units distribute leftover width],
)

== Header and Footer

#table(
  columns: (1fr, 1fr, 1fr),
  table.header([*Product*], [*Q1*], [*Q2*]),
  [Widget], [100], [150],
  [Gadget], [200], [180],
  [Gizmo], [50], [75],
  table.footer([*Total*], [*350*], [*405*]),
)

== Cell Spanning

#table(
  columns: 4,
  align: center,
  table.cell(colspan: 4)[*Annual Sales Report*],
  [*Region*], [*Q1*], [*Q2*], [*Total*],
  table.cell(rowspan: 2)[Americas], [120], [150], [270],
  [80], [95], [175],
  table.cell(rowspan: 2)[Europe], [200], [210], [410],
  [90], [100], [190],
)

== Styled: Zebra Stripes

#table(
  columns: (auto, 1fr, auto),
  fill: (_, y) => if calc.odd(y) { luma(240) },
  inset: 8pt,
  table.header([*ID*], [*Task*], [*Status*]),
  [1], [Design], [Done],
  [2], [Implement], [In progress],
  [3], [Test], [Pending],
  [4], [Deploy], [Pending],
)

== Styled: Header Highlight + Minimal Lines

#show table.cell.where(y: 0): strong

#table(
  columns: 3,
  stroke: none,
  inset: 8pt,
  fill: (_, y) => if y == 0 { blue.lighten(80%) },
  table.hline(stroke: 1.5pt),
  [Language], [Paradigm], [Year],
  table.hline(stroke: 0.5pt),
  [Rust], [Systems], [2010],
  [Typst], [Typesetting], [2023],
  [Python], [General], [1991],
  table.hline(stroke: 1.5pt),
)

== Grid Layout (No Borders)

#grid(
  columns: (1fr, 1fr),
  gutter: 16pt,
  [
    === Left Column
    Grids share the same API as tables but have no default strokes. Use them for layout rather than data display.
  ],
  [
    === Right Column
    Columns, rows, alignment, gutter, and cell spanning all work identically.
  ],
)

== Generated from Data

#let data = (
  (lang: "Rust", stars: "95k", license: "MIT/Apache"),
  (lang: "Typst", stars: "38k", license: "Apache 2.0"),
  (lang: "Zig", stars: "35k", license: "MIT"),
)

#table(
  columns: 3,
  [*Language*], [*GitHub Stars*], [*License*],
  ..data.map(r => ([#r.lang], [#r.stars], [#r.license])).flatten(),
)

== Figure-Wrapped Table

#figure(
  table(
    columns: (1fr, 1fr),
    table.header([*Input*], [*Output*]),
    [$x$], [$x^2$],
    [1], [1],
    [2], [4],
    [3], [9],
  ),
  caption: [Squared values.],
) <tab:squared>

See @tab:squared for the mapping.
