#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
#let rows = json("data.json")
#table(
  columns: 3,
  [*Name*], [*Price*], [*Stock*],
  ..rows.map(r => (r.name, str(r.price), str(r.stock)).map(x => [#x])).flatten(),
)
EOF
typst compile /app/main.typ /app/main.pdf
