#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
#let sales = json(bytes("{\"q1\": 120, \"q2\": 95, \"q3\": 143}"))

#set page(paper: "a4", margin: 2cm, header: context {
  let heads = query(heading.where(level: 1))
  if heads.len() > 0 { emph(heads.last().body) }
})

#show heading: it => context {
  let sz = measure(it).width
  it
}

= Quarterly Report

#table(
  columns: 2,
  [*Quarter*], [*Revenue*],
  [Q1], [#sales.q1],
  [Q2], [#sales.q2],
  [Q3], [#sales.q3],
)

#figure(
  curve(
    stroke: 1.5pt,
    curve.move((0pt, 30pt)),
    curve.line((40pt, 10pt)),
    curve.line((80pt, 20pt)),
  ),
  caption: [Trend],
)

#rect(width: 100%, height: 20pt, fill: tiling(size: (8pt, 8pt))[#line(start: (0pt, 8pt), end: (8pt, 0pt))])
EOF
typst compile /app/main.typ /app/main.pdf
