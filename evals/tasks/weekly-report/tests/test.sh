#!/bin/bash
# Pass when: main.typ compiles and contains exactly the required structure:
# 1 h1 title, 2 h2 sections, 1 table, 1 numbered (block) equation.
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

check() {  # check <description> <typst-expr> <expected>
  local desc="$1" expr="$2" want="$3"
  local got
  got=$(typst eval --in main.typ "$expr" 2>/dev/null || echo "eval-error")
  [ "$got" = "$want" ] || fail "$desc: want $want, got $got"
}

check "h1 count" 'query(heading.where(level: 1)).len()' 1
check "h2 count" 'query(heading.where(level: 2)).len()' 2
check "table count" 'query(table).len()' 1
check "block equation count" 'query(math.equation.where(block: true)).len()' 1
check "equation numbered" 'query(math.equation.where(block: true)).first().numbering != none' true

echo "1" > /logs/verifier/reward.txt
echo PASS
