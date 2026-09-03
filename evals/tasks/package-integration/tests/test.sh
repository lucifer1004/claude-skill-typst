#!/bin/bash
# Pass when: main.typ compiles, imports a preview package, and the rendered
# PDF shows the three task names plus a Jan/Feb timeline.
set -u
mkdir -p /logs/verifier

fail() {
  echo "0" > /logs/verifier/reward.txt
  echo "FAIL: $1"
  exit 0
}

[ -f /app/main.typ ] || fail "main.typ missing"
grep -q '@preview/' /app/main.typ || fail "no @preview package import"
cd /app
typst compile main.typ main.pdf 2>compile.err || fail "does not compile: $(head -3 compile.err)"

text=$(pdftotext main.pdf -)
for needle in "Design" "Implementation" "Testing" "Jan" "Feb"; do
  echo "$text" | grep -q "$needle" || fail "rendered output missing: $needle"
done

echo "1" > /logs/verifier/reward.txt
echo PASS
