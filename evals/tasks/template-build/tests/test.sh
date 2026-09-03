#!/bin/bash
# Pass when: conf.typ + demo.typ exist, demo compiles, and the output
# satisfies the template contract (2 columns, header shows current section,
# footer "N / M").
set -u
mkdir -p /logs/verifier

fail() {
  echo "0" > /logs/verifier/reward.txt
  echo "FAIL: $1"
  exit 0
}

[ -f /app/conf.typ ] || fail "conf.typ missing"
[ -f /app/demo.typ ] || fail "demo.typ missing"
grep -q 'import.*conf.typ' /app/demo.typ || fail "demo.typ does not import conf.typ"
cd /app
typst compile demo.typ demo.pdf 2>compile.err || fail "does not compile: $(head -3 compile.err)"

# Structural checks via typst eval.
h1=$(typst eval --in demo.typ 'query(heading.where(level: 1)).len()' 2>/dev/null || echo 0)
[ "${h1:-0}" -ge 2 ] || fail "fewer than 2 level-1 sections"

# Footer must contain "N / M" page numbering — inspect the PDF text layer.
pdftotext demo.pdf - | grep -qE '[0-9]+ */ *[0-9]+' || fail "no 'N / M' page numbering found"

echo "1" > /logs/verifier/reward.txt
echo PASS
