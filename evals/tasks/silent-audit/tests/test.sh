#!/bin/bash
# Partial credit via reward.json — one point per fixed trap, and a penalty
# check for the false alarm (Phi^(-1)(x) must stay correct).
set -u
mkdir -p /logs/verifier

write_reward() {
  python3 -c "
import json
json.dump({'accuracy': $1}, open('/logs/verifier/reward.json', 'w'))
"
}

[ -f /app/main.typ ] || { echo "FAIL: main.typ missing"; write_reward 0; exit 0; }
cd /app
if ! typst compile main.typ main.pdf 2>compile.err; then
  echo "FAIL: does not compile: $(head -3 compile.err)"
  write_reward 0
  exit 0
fi
if ! typst compile --features html main.typ main.html 2>/dev/null; then
  echo "FAIL: html export failed"
  write_reward 0
  exit 0
fi

python3 - <<'EOF'
import json
import re

html = open("/app/main.html").read()
checks = {}

# Trap 1: alpha_c(N) — the subscript must not contain the parenthesised arg.
msubs = re.findall(r"<msub>.*?</msub>", html, re.S)
checks["script_swallow"] = bool(msubs) and not any("<mo>(</mo>" in m for m in msubs)

# Trap 2: cal(Z)(tilde(S)) / cal(Z)(0) — a fraction whose denominator holds 0.
mfracs = re.findall(r"<mfrac>.*?</mfrac>", html, re.S)
checks["fraction_binding"] = any(
    re.search(r"<m[ion][^>]*>0</m[ion]>", f) for f in mfracs
)

# Trap 3: "--" in math must become an en-dash (either a literal – or dash.en).
checks["en_dash"] = "<mtext>--</mtext>" not in html

# False alarm: Phi^(-1)(x) must NOT be mangled — superscript exists, and no
# parenthesis group may be folded into the superscript.
msups = re.findall(r"<msup>.*?</msup>", html, re.S)
checks["false_alarm_intact"] = bool(msups) and not any(
    "<mo>(</mo>" in s for s in msups
)

score = sum(checks.values()) / len(checks)
print(json.dumps(checks, indent=2))
json.dump({"accuracy": score}, open("/logs/verifier/reward.json", "w"))
EOF

[ -f /logs/verifier/reward.json ] || write_reward 0
