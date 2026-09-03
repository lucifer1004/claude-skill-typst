#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
#set page(paper: "a4", margin: 2cm, footer: context {
  let total = counter(page).final().first()
  let current = counter(page).get().first()
  [Page #current of #total]
})

= Alpha

#lorem(400)

#pagebreak()

= Beta

#lorem(400)
EOF
typst compile /app/main.typ /app/main.pdf
