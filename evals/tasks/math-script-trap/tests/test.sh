#!/bin/bash
# Pass when: main.typ compiles AND the subscript does not contain the
# parenthesised argument (checked via the MathML emitted by HTML export).
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
typst compile --features html main.typ main.html 2>/dev/null || fail "html export failed"

python3 - <<'EOF'
import re

html = open("/app/main.html").read()
msubs = re.findall(r"<msub>.*?</msub>", html, re.S)
if not msubs:
    print("FAIL: no subscript found")
    raise SystemExit(0)
for m in msubs:
    if "<mo>(</mo>" in m:
        print("FAIL: argument folded into subscript:", m[:120])
        raise SystemExit(0)
print("PASS")
open("/logs/verifier/reward.txt", "w").write("1")
EOF

[ -f /logs/verifier/reward.txt ] || echo "0" > /logs/verifier/reward.txt
