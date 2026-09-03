#!/bin/bash
# Pass when: main.typ compiles and contains the modern equivalents of each
# removed API used by the 0.12 draft.
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

# Removed APIs must be gone from the source.
for gone in 'json\.decode' '\blocate\(' '\bstyle\(' '\bmeasure([^)]*styles' '\bpattern\(' '#path\('; do
  if grep -qE "$gone" main.typ; then
    fail "removed API still present: $gone"
  fi
done

# Modern replacements must be present.
grep -qE '\bcurve\(|\bline\(' main.typ || fail "no drawing element (curve/line)"
grep -q 'context' main.typ || fail "no context expression (locate/style replacement)"
grep -q 'json(' main.typ || fail "json() call missing"

# Data must survive the migration.
n=$(typst eval --in main.typ 'query(table).len()' 2>/dev/null || echo 0)
[ "${n:-0}" -ge 1 ] || fail "no table element found"

echo "1" > /logs/verifier/reward.txt
echo PASS
