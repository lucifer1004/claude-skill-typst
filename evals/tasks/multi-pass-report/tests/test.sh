#!/bin/bash
# Pass when: main.typ compiles to a multi-page PDF whose footer shows the
# correct "Page X of N" on every page, with N equal to the real page count.
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

pages=$(pdfinfo main.pdf | awk '/^Pages:/ {print $2}')
[ "${pages:-0}" -ge 2 ] || fail "document has fewer than 2 pages"

text=$(pdftotext main.pdf -)
for p in $(seq 1 "$pages"); do
  echo "$text" | grep -qE "Page $p of $pages" || fail "missing 'Page $p of $pages'"
done

echo "1" > /logs/verifier/reward.txt
echo PASS
