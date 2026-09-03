#!/bin/bash
# Pass when: main.typ compiles and the document contains a table whose
# content mentions all four product names from data.json.
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

n=$(typst eval --in main.typ 'query(table).len()' 2>/dev/null || echo 0)
[ "${n:-0}" -ge 1 ] || fail "no table element found"

typst compile --features html main.typ main.html 2>/dev/null || fail "html export failed"
for name in Widget Gadget Sprocket Doohickey; do
  grep -q "$name" main.html || fail "product $name missing from rendered output"
done

echo "1" > /logs/verifier/reward.txt
echo PASS
