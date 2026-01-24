#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt)

= Typst Perf Test

#let make-table(rows) = {
  let cells = ()
  for r in rows {
    cells.push([#r])
    cells.push([#(r * 2)])
    cells.push([#(r * r)])
  }

  table(
    columns: (auto, 1fr, 1fr),
    [*Index*], [*Value*], [*Square*],
    ..cells,
  )
}

#let section(i) = [
  == Section #i #label("sec-" + str(i))
  #lorem(80)

  #let items = range(1, 12).map(n => n + i)
  #make-table(items)

  #let sum = items.fold(0, (acc, x) => acc + x)
  Total: #sum

  #if calc.rem(i, 3) == 0 {
    [*Note:* This section triggers an extra block.]
  }
]

#for i in range(1, 40) {
  section(i)
  pagebreak(weak: true)
}

== Summary

#context {
  let hs = query(heading.where(level: 2))
  [Total sections: #hs.len()]
}
