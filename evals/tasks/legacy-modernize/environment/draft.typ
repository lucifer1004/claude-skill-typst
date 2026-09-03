// Written for Typst 0.12. Does not compile on current Typst.
#let sales = json.decode(bytes("{\"q1\": 120, \"q2\": 95, \"q3\": 143}"))

#set page(paper: "a4", margin: 2cm, header: locate(loc => {
  let heads = query(heading.where(level: 1), loc)
  if heads.len() > 0 { emph(heads.last().body) }
}))

#show heading: it => style(styles => {
  let sz = measure(it, styles).width
  it
})

= Quarterly Report

#table(
  columns: 2,
  [*Quarter*], [*Revenue*],
  [Q1], [#sales.q1],
  [Q2], [#sales.q2],
  [Q3], [#sales.q3],
)

#figure(
  path((0pt, 30pt), (40pt, 10pt), (80pt, 20pt), stroke: 1.5pt),
  caption: [Trend],
)

#rect(width: 100%, height: 20pt, fill: pattern(size: (8pt, 8pt))[#line(start: (0pt, 8pt), end: (8pt, 0pt))])
