#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
#curve(
  stroke: 1pt,
  curve.move((0pt, 0pt)),
  curve.line((60pt, 20pt)),
  curve.line((120pt, 0pt)),
)
EOF
typst compile /app/main.typ /app/main.pdf
