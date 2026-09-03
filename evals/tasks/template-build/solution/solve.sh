#!/bin/bash
set -euo pipefail
cat > /app/conf.typ <<'EOF'
#let conf-paper(title: "", authors: (), body) = {
  set page(
    paper: "a4",
    margin: 2cm,
    header: context {
      let heads = query(heading.where(level: 1).before(here()))
      if heads.len() > 0 { emph(heads.last().body) }
    },
    footer: context {
      let n = counter(page).final().first()
      [#counter(page).get().first() / #n]
    },
  )
  set text(size: 10pt)
  align(center, text(17pt, strong(title)))
  align(center, authors.join(", "))
  columns(2, body)
}
EOF
cat > /app/demo.typ <<'EOF'
#import "conf.typ": conf-paper

#show: conf-paper.with(
  title: "A Study of Nothing in Particular",
  authors: ("Alice", "Bob"),
)

= Introduction

#lorem(120)

= Methods

#lorem(120)
EOF
cd /app && typst compile demo.typ demo.pdf
