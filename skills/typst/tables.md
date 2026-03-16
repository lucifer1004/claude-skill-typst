# Tables and Grids

For page layout and styling, see [styling.md](styling.md). For data types, see [types.md](types.md).

## Basic Table

```typst
#table(
  columns: 3,
  [*Name*], [*Age*], [*City*],
  [Alice], [30], [Berlin],
  [Bob], [25], [Tokyo],
)
```

## Column Sizing

```typst
// Fixed widths
#table(columns: (3cm, 5cm, auto))

// Fractional (like CSS flex)
#table(columns: (1fr, 2fr, 1fr))

// Mixed
#table(columns: (auto, 1fr, 80pt))

// Equal fractions shorthand
#table(columns: (1fr,) * 4)
```

## Alignment

```typst
// Per-column alignment
#table(
  columns: 3,
  align: (left, center, right),
  [Left], [Center], [Right],
  [text], [text], [text],
)

// Single alignment for all cells
#table(columns: 2, align: center, [A], [B], [C], [D])
```

## Header and Footer Rows

```typst
#table(
  columns: (1fr, 1fr, 1fr),
  table.header(
    [*Product*], [*Q1*], [*Q2*],
  ),
  [Widget], [100], [150],
  [Gadget], [200], [180],
  table.footer(
    [*Total*], [*300*], [*330*],
  ),
)
```

`table.header` repeats on every page. `table.footer` repeats at bottom of every page.

## Cell Spanning

```typst
#table(
  columns: 3,
  table.header(
    table.cell(colspan: 3, align: center)[*Sales Report*],
    [*Region*], [*Q1*], [*Q2*],
  ),
  [North], [120], [150],
  [South], [80], [95],
  table.cell(colspan: 2)[Subtotal], [445],
)
```

### Row Spanning

```typst
#table(
  columns: 3,
  [*Category*], [*Item*], [*Price*],
  table.cell(rowspan: 2)[Fruit], [Apple], [1.20],
  [Banana], [0.80],
  table.cell(rowspan: 2)[Dairy], [Milk], [2.50],
  [Cheese], [4.00],
)
```

## Stroke (Borders)

```typst
// No borders
#table(columns: 2, stroke: none, [A], [B], [C], [D])

// All borders with specific color and thickness
#table(columns: 2, stroke: 0.5pt + gray, [A], [B], [C], [D])

// Only horizontal lines
#table(
  columns: 2,
  stroke: (x: none, y: 0.5pt),
  [A], [B], [C], [D],
)
```

### Per-Cell Stroke

```typst
#table(
  columns: 3,
  stroke: none,
  table.hline(),
  [*A*], [*B*], [*C*],
  table.hline(),
  [1], [2], [3],
  [4], [5], [6],
  table.hline(),
)
```

### Horizontal and Vertical Lines

```typst
#table(
  columns: 3,
  stroke: none,
  table.hline(stroke: 2pt),            // Top border
  [*Name*], [*Score*], [*Grade*],
  table.hline(stroke: 0.5pt),          // Under header
  [Alice], [95], [A],
  [Bob], [82], [B],
  table.hline(stroke: 2pt),            // Bottom border
)
```

```typst
#table(
  columns: 3,
  stroke: none,
  table.vline(x: 1),                   // Line before column 1
  [Label], [Value 1], [Value 2],
  [X], [10], [20],
)
```

## Fill (Background Color)

```typst
// Alternating row colors
#table(
  columns: 3,
  fill: (_, y) => if calc.odd(y) { luma(240) },
  table.header([*A*], [*B*], [*C*]),
  [1], [2], [3],
  [4], [5], [6],
  [7], [8], [9],
)
```

```typst
// Header fill
#table(
  columns: 2,
  fill: (_, y) => if y == 0 { blue.lighten(80%) },
  [*Key*], [*Value*],
  [Name], [Alice],
  [Role], [Engineer],
)
```

### Per-Cell Fill

```typst
#table(
  columns: 3,
  [Normal], table.cell(fill: yellow)[Highlighted], [Normal],
  [A], [B], [C],
)
```

## Inset and Gutter

```typst
// Cell padding
#table(columns: 2, inset: 10pt, [Roomy], [Cells])

// Asymmetric inset
#table(columns: 2, inset: (x: 12pt, y: 6pt), [Wide], [Padding])

// Gutter (space between cells, outside borders)
#table(columns: 3, gutter: 3pt, [A], [B], [C])

// Column/row gutter separately
#table(columns: 2, column-gutter: 5pt, row-gutter: 2pt, [A], [B], [C], [D])
```

## Set Rules for Tables

Apply defaults to all tables in scope:

```typst
#set table(stroke: 0.5pt + luma(180), inset: 8pt)
#show table.cell.where(y: 0): strong

// All subsequent tables get these defaults
#table(columns: 2, [*Key*], [*Value*], [A], [1])
```

## Grid (Layout Without Borders)

`grid()` has the same API as `table()` but no default strokes — use it for layout.

```typst
#grid(
  columns: (1fr, 1fr),
  gutter: 16pt,
  [
    == Left Column
    First block of content.
  ],
  [
    == Right Column
    Second block of content.
  ],
)
```

### Grid for Aligned Forms

```typst
#grid(
  columns: (auto, 1fr),
  gutter: 8pt,
  [*Name:*], [Alice Johnson],
  [*Email:*], [alice\@example.com],
  [*Role:*], [Engineer],
)
```

## Generating Tables from Data

```typst
#let data = (
  (name: "Alice", score: 95),
  (name: "Bob", score: 82),
  (name: "Carol", score: 91),
)

#table(
  columns: 2,
  [*Name*], [*Score*],
  ..data.map(row => (row.name, str(row.score))).flatten(),
)
```

## Common Patterns

| Pattern             | Code                                                  |
| ------------------- | ----------------------------------------------------- |
| Borderless table    | `#table(stroke: none, ...)`                           |
| Header-only borders | `stroke: none` + `table.hline()` around header        |
| Zebra stripes       | `fill: (_, y) => if calc.odd(y) { luma(240) }`        |
| Bold header row     | `#show table.cell.where(y: 0): strong`                |
| Caption + label     | Wrap in `#figure(table(...), caption: [...]) <label>` |
| Full-width table    | `columns: (1fr,) * n`                                 |
| Centering a table   | `#align(center, table(...))`                          |
