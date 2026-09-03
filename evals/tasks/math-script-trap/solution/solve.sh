#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
$ alpha_c (N) = 1/N $
EOF
typst compile /app/main.typ /app/main.pdf
