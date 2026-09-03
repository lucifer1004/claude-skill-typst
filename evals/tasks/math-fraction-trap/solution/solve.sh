#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
$ frac(cal(Z)(tilde(S)), cal(Z)(0)) $
EOF
typst compile /app/main.typ /app/main.pdf
