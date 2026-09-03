#!/bin/bash
# Pass when: main.typ compiles AND an <mfrac> exists whose denominator
# contains the "0" (i.e. the whole cal(Z)(0) is under the bar).
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
mfracs = re.findall(r"<mfrac>.*?</mfrac>", html, re.S)
for f in mfracs:
    if re.search(r"<m[ion][^>]*>0</m[ion]>", f):
        print("PASS")
        open("/logs/verifier/reward.txt", "w").write("1")
        raise SystemExit(0)
print("FAIL: no fraction with 0 in the denominator; mfracs:", [f[:100] for f in mfracs])
EOF

[ -f /logs/verifier/reward.txt ] || echo "0" > /logs/verifier/reward.txt
