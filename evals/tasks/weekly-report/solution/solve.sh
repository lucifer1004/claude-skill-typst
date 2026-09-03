#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
#set page(paper: "a4", margin: 2cm)
#set math.equation(numbering: "(1)")

= Weekly Status Report

== Progress

#table(
  columns: 2,
  [*Task*], [*Status*],
  [API migration], [Done],
  [Benchmark suite], [In progress],
  [Documentation], [In progress],
)

== Plans

Next week we will finish the benchmark suite and draft the release notes.

$ E = m c^2 $
EOF
typst compile /app/main.typ /app/main.pdf
