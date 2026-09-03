#!/bin/bash
# Pass when: main.typ compiles to a PDF and the document contains at least
# one drawing element (curve or line).
set -u
mkdir -p /logs/verifier

fail() {
  echo "0" > /logs/verifier/reward.txt
  echo "FAIL: $1"
  exit 0
}

[ -f /app/main.typ ] || fail "main.typ missing"
cd /app
typst compile main.typ main.pdf 2>compile.err || fail "does not compile: $(head -3 compile.err)"

grep -qE '\b(curve|line|polygon)\(' main.typ || fail "no drawing element (curve/line/polygon) in source"
echo "1" > /logs/verifier/reward.txt
echo PASS
